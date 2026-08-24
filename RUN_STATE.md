# JouleWise Run State

This file is the single running pointer for the project: the one doc to
read to get back here. Session records live in `docs/run_reports/` and
`docs/process_traces/`; deliberation lives in `docs/council_log.md`;
policy lives in `docs/decision_log.md`. The three dated restart docs
`docs/process_traces/RESUME-2026-07-26.md`, `RESUME-2026-07-27.md`, and
`RESUME-2026-07-28.md` are now point-in-time session records only — each
carries a superseded banner, and everything still current in them is
folded in below. Do not create another dated restart doc; update this
file instead.

Last updated: 2026-08-23 night (T22 — new calexits flake found+diagnosed, fix round in flight; S-0 clone head must be a GREEN run containing f6a4c81, so the flake fix is S-0-blocking; runsheet read DONE; Ed's prompts still the only human gate)

**T22 NIGHT — CALEXITS-MUTATION-FLAKE:** a NEW intermittent CI failure
class opened after the merge wave: `calibration-exits-exclusive` fails
~50% (alternating interpreters) on
`test_forced_auto_maintenance_mutation_reproduces_cleanup_race`. Root
cause diagnosed at the bench from run 32677039329's trace2 dump: the
forced race reproduces in a THIRD shape the test's post-rmtree dichotomy
never modeled — clean rmtree AND the detached pack child killed during
`prepare-pack` ("object cannot be read", exit 128) before any
`write-pack-file` region; the else-branch assertion and
`_classify_pack_cleanup` (empty-intervals -> TRACE_INCOMPLETE) both
reject it, though it is race-exercised evidence. Ruled fix (third
terminal shape -> RACE_EXERCISED; widened assertion via shared helper;
deterministic classifier unit tests) delegated to the ackfix agent in
-wt-ackfix; magistrate reviews before landing. CI status: last all-green
head is eeeaf94; f6a4c81 + f692e26 failed on the flake; tip 33aa594
in_progress. S-0 IMPLICATION: the clone head must be a green run
containing f6a4c81 (the pinset-builder fix), so S-0 waits on this fix
landing green — Ed's freeze-prompt sitting remains the only HUMAN gate.

**T22 EVENING:** CI GREEN at 42df510 (conclusion-field-verified) after
three post-merge cures (stale S1D-1 test rewritten to pin the ruled
surface; the 3.14 argparse/Mock-stdout fixture fix; the ack-nominal
1s->4s cure in both consumers — sixth-firing class CLOSED). KERNEL
WAVE c749224: S1-CANDIDATE-01 + CALWRITER-ACK-TIMEOUT-01 closed on
green evidence; A84 FIXTURE-MODERNIZATION-01 + A85 MLX-ACID-SIGABRT-01
registered; 87 live. CI hill-climb runs under the A+B shape
(Monitor-shell, commit-first sub-40-min turns; levers 1+6 landed —
memo 3.3-3.5x + the nominal cure; turns A-D staged for levers 2-5).
S-0 PRECONDITIONS ALL MET except: (a) the lead's one-sitting
pre-execution read of s0-runsheet-r2 at the execution head (closes
S0-RUNSHEET-R2; includes the anchor re-verification the pin note
assigns); (b) Ed at the keyboard for the freeze-command permission
prompts. Then: Ed's pre-campaign REBOOT (D-150a) -> the real
transaction with step-6 under the D-150b delegation -> READY sitting
-> windows.

**T22 (2026-08-23 afternoon):** the RULE-1 GATE CLOSED (8-slice read
ledger, candidate SOUND) and the MERGE WAVE LANDED: S-1 (3c098de, the
full D-151+marker implementation), the ack-driver H4 fix (fe53aef),
the calexits 7-item hardening (e6a6520) — CI adjudicating
(conclusion-field-verified only, per E-1). Ed rulings D-150a
(pre-campaign REBOOT then no-reboot span; push freeze with the
committed visibility/notification protocol) and D-150b (STEP-6 +
TERMINAL REVIEW DELEGATED to the magistrate as
independence-preserving mechanical comparison; Ed notified, never
blocked-on) recorded and pushed. CI hill-climb ROUND 2 running on Sol
xhigh (target <=12 min; perf/test-speed, watchdogged). NEXT IN ORDER:
(1) CI green on e6a6520 -> kernel wave (close S1-CANDIDATE-01;
register A84 + A85 from the corrected packet rows); (2) my full
pre-execution read of s0-runsheet-r2 + strike the 21-test addendum +
pin update to e6a6520 (closes S0-RUNSHEET-R2); (3) S-0 AT THE BENCH —
needs Ed's permission-prompt clicks (or the optional settings rule);
(4) Ed's pre-campaign REBOOT (D-150a); (5) the REAL transaction
(S-1..S-5 commits per r4-3) with step-6 under the D-150b delegation;
(6) READY sitting -> windows -> the paper's data.

Last updated (T21 morning): (S-1 gauntlet-complete at b5f97c3)

**T21 MORNING CLOSE:** the S-1 candidate finished its complete
adversarial arc: conformance audit → finish round → G-11 cure →
independent Opus seat (REFUTED, 3 blockers) + Sol G-2 refuter
(REFUTED, impersonation channel) → combined fix round (all four
blockers cured; G2-1 six-bypass-verified) → close-out (repo radius
3746 passed / 0 failures; 4 fix-round defects self-found via AST
sweep) → DELTA RE-AUDIT: ACCEPT, no blockers, 6 bench conditions —
ALL APPLIED at b5f97c3 (pushed). Delta rulings of record: the widened
authoring fence ADMISSIBLE (2026-08-12 cold-gate semantic boundary +
D-134 cl.6 + T-0 precedent); the hC operator-residual must NOT be
mechanized (D-151 fixed-point tripwire — S-0 runsheet carries the
operator-discipline line; literal pins at post-window fixation);
S0-BLOCKED partition independently confirmed 0/17/4 honest. NEXT, in
order: (1) THE LEAD'S FULL READ of main...impl/s1-candidate (rule 1;
fresh context required — do NOT skim it at the end of a long session);
(2) merge-ability/overbuild prune at the same read; (3) kernel wave:
register A84 FIXTURE-MODERNIZATION-01 + A85 MLX-ACID-SIGABRT-01
(paste-ready rows in docs/process_traces/2026-08-22-t20/s1-candidate/
s1-fixround-packet.md, corrected a500378) + close S1-CANDIDATE-01 on
its acceptance; (4) merge under D-148.2 gates; (5) my full pre-S-0
read of s0-runsheet-r2 (closes S0-RUNSHEET-R2) + pin update to the
merged head + strike the 21-test addendum per ruling; (6) S-0 AT THE
BENCH with Ed live prompts. Parallel harvests COMPLETE: ack-fix
e2e5605 VERIFIED-READY (H4 protocol confirmed, 4-mutant kill matrix,
pinset hash-verified) + calexits 0202ce9 VERIFIED-READY (7/7, E-4
fence byte-held) + COMBINED-GREEN integration run (both coupled
modules pass in the merged state; shared harness same-blob on all four
refs). ALL FOUR BRANCHES now wait ONLY on lead gates: S-1 full read,
speed-branch review, then the merge wave (D-148.2) + kernel wave
(A84/A85 + closures + the 6.2x memo lever and _WITNESS_RESULTS rows).

Last updated (previous): 2026-08-23 early AM (T21 overnight fan-out — ALL WORK PRESERVED ON PUSHED BRANCHES; harvest orders below)

**T21 OVERNIGHT (2026-08-23 ~01:00-06:30):** Ed licensed full Codex
spend + Workflows + the Opus hill-climb directive (memory saved). The
S-1 gauntlet ran its full arc: conformance audit (10 gaps) -> finish
round (G-2/3/4 cured) -> G-11 cure (135 red -> 4; S0-BLOCKED measured
EMPTY — two seats agree the 21-test theory was wrong) -> independent
Opus seat REFUTED (3 blockers) + Sol G-2 refuter REFUTED
(impersonation channel) -> COMBINED FIX ROUND: G2-1 impersonation
channel CLOSED, six-bypass-verified, no-CLI-derivation fence held;
B-1 re-derivation proven LIVE (V-1(iii) intact); B-2 skips
machine-readable. PRESERVED: impl/s1-candidate @ d3101d6 (WIP — the
commit message IS the harvest order: seam cure check, joint
verification, MANIFEST rewrite, then DELTA RE-AUDIT; packet with
kernel rows A84/A85 custodied under
docs/process_traces/2026-08-22-t20/s1-candidate/).
fix/sampler-ack-timeout @ e2e5605 (WIP, UNVERIFIED — run both consumer
modules + pinned-file check). fix/calexits-hygiene (7/7 committed,
re-verify then PR). perf/test-speed (5 commits, CI 41->23.5 min
measured, lead review pending; register the 6.2x test_reduce memo
lever + the _WITNESS_RESULTS fragility row; 14-day 2-core CPU leak
KILLED ~03:15 — all bench timings before that ran 2 cores short).
Orchestrator deaths overnight were CONTEXT EXHAUSTION, not transport;
the Sol transport advisory stands until Ed restarts the Codex app.

Last updated (previous): 2026-08-22 evening (T20 — THE `_v4` TRANSACTION IS OPEN; mint license granted; next: kernel registrations → S-1 candidate stream → S-0 at the bench)

**T20 (2026-08-22) — the day the transaction opened.** Ed granted the
MINT LICENSE in-session and ruled packet items 1-4 (D-150, 73764f0:
license = live prompts at Ed's hands, NO settings rule exists and none
is required; HORIZON 168h; V6 marker option (a) custody-external;
B-δ = unattended-T-0 work order T0-UNATTENDED-01 authorized — `_v4`
windows gate on its landing). S-0 clone-proof runsheet assembled
(docs/process_traces/2026-08-22-t20/s0-runsheet-r1.md, lead full read;
poison question YES → sacrificial pre-mint step; needs r2 revision per
the rulings below — r1 custodied as-assembled, pre-D-151/marker).
O-1 (pinset growth vs byte-pin) RULED via a three-round cold gate with
a full double-crossover: D-151 (2a9257d) — O-1-D versioned-successor
pinset, successor path = 112th allowlist entry, digest-conditional on
Ed's step-6 confirmation table, post-window fixation, two-part
published-green, standing fixed-point rule (no authenticator path ever
enters any allowlist). Marker co-design RULED (a3f2edf): unified
step-6 table joins marker + pinset authentication (ONE Ed yes);
strict four-way head equality; library-boundary publication gate;
scheduler receipt v2 with G7 (schedgate-ruling amended to seven
gates). PAPER: results-fill registry RE-BOUND to the post-#166 draft
and LANDED (1afb9ce, 42 rows, full gauntlet; custody
docs/process_traces/2026-08-22-t20/registry-rebind-r2.md). CLOSURES:
A78 N-5-RECORD-AMENDMENT (77f01e5, refuted→cured→delta-ACCEPT);
CALEXITS-TIMING-HYGIENE (audit
docs/process_traces/2026-08-22-t20/calexits-timing-audit.md — 7
mechanisms separate, H1–H9, successor row CALEXITS-HYGIENE-FIXES-01;
Opus closure refuter SURVIVES with 2 should-fix, both cured + delta-ACCEPT; kernel 83 live). README refreshed
(1ba04a8). NEXT IN ORDER: (1) kernel txn registering T0-UNATTENDED-01
+ S1-CANDIDATE-01 (= D-151 conds 1/2/6/8 + marker-ruling
consequences) + S0-RUNSHEET-R2 — DONE at 6693cfa (+ the
CALWRITER-ACK-TIMEOUT-01 flake row at the T20 close-out; run report
docs/run_reports/2026-08-22-t20-session.md is THE session record,
incl. the four-red-run CI incident + dispositions + ERRATA E-1: the 97e0203 SUCCESS claim was false — cure held, but a new #121-class race reds the shard, row EVIDENCE-AUTHOR-GIT-TEARDOWN-01); (2) the S-1 reviewed-candidate
implementation stream — SUBSTANTIALLY IMPLEMENTED and PRESERVED at
impl/s1-candidate bd7ebc1 (pushed; WIP, NOT reviewed/gauntleted: all
six new files + ~1,700 modified lines, 87 tests OK lead-run across the
four touched modules; the implementing Sol thread stalled at the
manifest stage — the day's FOURTH transport stall; NEEDS_SCOPE arc +
v2-registry-coordinate ruling + successor-pinset path adjudication all
recorded in this session). GAUNTLET IN PROGRESS: conformance
audit DONE (Opus; 10 gaps G-1..G-10); finish round DONE (G-2/3/4
blockers cured, 7 commits); G-11 round DONE (the ruled v1->v2 repoint
red 135 tests -> 4; head c1b87f6 PUSHED; whole 28-module radius 1368
tests / 2F+2E / 21 enumerated S0-BLOCKED expected failures; frozen
surfaces IDENTICAL). OPEN FINDING for the independent seat (MANIFEST
9.3.6): R1 reviewed-HEAD gates make the authoring re-derivation
refusal (:5470 family) fixture-unreachable — subsumed-by-design vs
over-broad-gate, 4 staged failing tests as fixtures. INDEPENDENT
writer-not-reviewer SEAT RUNNING (Opus). Then: lead full read ->
patch+sidecar export -> land -> S0-RUNSHEET-R2 -> S-0 at the bench. TRANSPORT ADVISORY: MCP codex server
(up since 08-09) + CLI bridge both degraded — Ed should restart the
Codex desktop app/server before the next delegated wave;
(3) S-0 EXECUTED AT THE LEAD'S BENCH in a throwaway clone (Ed
approves freeze-command prompts live); (4) S-2..S-5 per r4-7.
Codex desktop app down → standalone CLI fallback (audited, no pet);
two Sol background review runs wedged on that transport today —
prefer MCP route or Opus for reviews until the app returns.

**T19.3 (~06:15 PDT):** calexits closures LANDED (1a15172): CI311 retired
(fix aedf530 CI-green at b01d9a2 + E-4 retro-review UPHELD),
CENSUS-PIDRACE retired (b01d9a2). Consistency sweep applied (4 findings,
6649736); ERRATA E-5 filed (39MB tarball transited history via a git
add -A miss — Ed decides on rewrite; bookkeeping now stages by pathspec
only). Open low-priority rows: N-5-RECORD-AMENDMENT (substance largely
satisfied by the T19.2 addendum + cold custody; closure is bookkeeping),
CALEXITS-TIMING-HYGIENE umbrella. EVERYTHING ED-INDEPENDENT ON THE
CRITICAL PATH IS DONE — the queue rides the _v4 boundary, which rides
ED PACKET ITEM 1 (mint license). Ledger: runs 51-69, pool ~21%.

**T19.2 (2026-08-21 ~03:50 PDT):** PR #166 MERGED (0c3c1a6) — the paper's
replication-bar rewrite (pedagogy round 4, 12 fixed + 9 evidence-fenced)
behind a full D-118 gate ledger. PR #167 MERGED (cd50dc7) —
RECEIPT-HISTSEM-01, landed BEFORE the _v4 re-freeze per ruling: 4 fix
rounds, 3 delta re-audits, a rule-11 consult (round 3's design), and an
Opus counter-review that caught a real blocker (symlinked-predecessor gate
disengagement) — gate item 6 is not optional. Cold-pair arc on the gate
question custodied in cold-pair-166/ (the Opus refuter overturned the cold
severance ruling; gate satisfied directly instead). Calexits: CI 3.11
errno fix on main (aedf530, ERRATA E-2/E-4 corrections of record); four
defect rows registered in TASK_QUEUE (CI311 / CENSUS-PIDRACE / N-5
amendment / TIMING-HYGIENE umbrella). Session envelopes + codex ledger
(runs 51-66) in t19-envelopes/. Kernel closure transaction LANDED this block (RECEIPT-HISTSEM-01 retired; four calexits rows registered); skill-usage log written; run-report T19.2 note LANDED (2a89ea1). _v4 REMAINS BLOCKED SOLELY ON
ED PACKET ITEM 1 (mint license). Codex pool ~20% used, resets 08-27.

**T19.1 (successor session, ~20:05 PDT):** the RH refuter survived the
/clear and is STILL RUNNING (watched; harvest on completion). The T18/T19
run-report addendum is LANDED (`docs/run_reports/2026-08-20-t18-t19-session.md`)
with a custody erratum (`…go-session/ERRATA.md` E-1: the rh-impl-report
branch field is wrong — the work is on `impl/receipt-histsem` @ 60ba2e9).
Corrections of record vs the checkpoint below: codex usage reads 16.0%
(not ~15%); #164/#165 merged 2026-08-21 in UTC.

## ▶▶ T19-CHECKPOINT (2026-08-20 ~19:50 PDT, Ed checkpoint order) — A FRESH SESSION STARTS HERE

**STATE IN ONE BREATH:** SIX gauntleted PRs merged today (#160 merge
wave, #161 scheduler gates, #162 FRE, #163 PTD, #164 RAC, #165 D-144
followups+prewindow), each behind a full-canonical gate; three
councils + four D-144 co-design rulings cold-ratified; the N-5
canonical flake root-caused and fixed *(amended 2026-08-22, cold-pair-166
R2.3: post-fix recurrence at a8f1549 under load; causation open)*; the B7 paper claim-integrity
ruling landed (stricter reading); kernel at 83 live rows; the `_v4`
transaction fully specced (r5 + the RH 112-path amendment) and
BLOCKED SOLELY ON ED PACKET ITEM 1 (mint license — the consolidated
10-item packet is in the T17 block above).

**IN FLIGHT AT CHECKPOINT (harvest, don't relaunch):**
- Branch `impl/receipt-histsem` (pushed): the RECEIPT-HISTSEM-01
  implementation, owning suites green, GAUNTLET IN PROGRESS — a
  terra xhigh refuter was mid-run writing to
  /private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/rh-refuter.md
  (that path persists on disk after /clear; poll its .status
  sibling). On SURVIVES: lead full read, add the annex-D16 ONE-home
  contract doc, PR + full-canonical merge gate, then the kernel
  closure row. On REFUTED: fix round per the day's pattern (delta
  re-audit after; two same-signature rounds = consult, rule 11).
- The ruling authority for that work: rh-ruling.md in the go-session
  custody (FINAL, cold-ratified, five fixes applied; its normative
  annexes bind).

**SUCCESSOR ORDER (after harvesting the refuter):**
1. Finish RECEIPT-HISTSEM (above). 2. Remaining unblocked queue rows
are thin — the big blocks (UNVERIFIED re-audits, SITTING2
preconditions, schedgate stages 3-6, the marker co-design) all ride
the `_v4` boundary or Ed rulings. 3. If Ed has installed the mint
license: OPEN THE `_v4` TRANSACTION per rulings-r5-consolidation.md
(S-0 lead-executed clone proof FIRST; the RH pinset + 112-path
allowlist amendments bind; V-7's packet order). 4. Otherwise: paper
program desk work (fidelity/pedagogy passes on the enriched draft
sections under the writing standard; figure-skeleton staging) and the
T18/T19 run-report addendum (the T17 report covers through midday;
the afternoon arc — the five later PRs, the RAC escalation, the flake,
RH — needs its dictated-fills addendum).

**Custody:** everything load-bearing is committed and pushed on main
through the RH ruling custody (42bd318) + this checkpoint; the
codex-run ledger (50 runs, ~15% of the weekly pool used, resets
2026-08-27) is custodied in the go-session dir. All session
worktrees/scratchpad are DISPOSABLE except as noted above (the
refuter output path). Standing cautions: the four r6-pinned files
(hazard block above); custody staging outside canonical-runner trees;
the WRITE_SCOPE literal line; one codex-run per background call.

## ▶▶ T18 (2026-08-20 evening) — AUTONOMOUS DRAIN DAY COMPLETE; EVERYTHING ED-INDEPENDENT ON THE CRITICAL PATH IS DONE

Merged today, each through the full gauntlet + a full-canonical merge
gate: #160 (the Phase-2 merge wave), #161 (scheduler gates stages 1-2,
D-144 co-designed + cold-ratified), #162 (FREEZE-REPLAY-EXPIRY-01),
#163 (PROC-TEARDOWN-01, incl. a frozen-surface remand — see the
standing hazard below), #164 (REAUTHOR-CLEAN-01 via a rule-11
escalation consult after two same-signature rounds). Also on main:
the N-5 order-dependent canonical flake root-caused and fixed
(46d710f) *(amended 2026-08-22 per cold-pair-166 R2.3: post-fix
recurrence at a8f1549 under concurrent load; incomplete-fix vs
load-induced left open — see the T18/T19 run report §2 amendment)*;
the B7 claim-integrity ruling (superseded-era magnitudes
left the paper, stricter reading, b7adb14); WINDOW_STATUS + paper cite
corrections; the T17 run report; the work-order kernel transaction
(83 live rows after the evening closure, 0f34a52).

Open lanes: D144-SEATPASS-FOLLOWUPS, RECEIPT-HISTSEM-01,
PREWINDOW-REGEX-01 (drain continues); the sitting's UNVERIFIED
re-audits + next-sitting preconditions ride the `_v4` boundary. The
`_v4` TRANSACTION REMAINS BLOCKED SOLELY ON ED PACKET ITEM 1 (the
mint-license settings rule); items 2-10 in the consolidated packet
above. Codex usage ~13-15% of the weekly pool; run ledger in the
session scratch.

## ▶▶ T17 (2026-08-20 morning, the GO session, MID-SESSION checkpoint) — THE MERGE WAVE IS ON MAIN; TWO COUNCILS RULED; FAN-OUT LIVE

**STATE IN ONE BREATH:** T16's four merge gates all went GREEN and the
wave LANDED — main @ 5bd7acf (PR #160) carries the full D-146/D-147
transaction. Gate custody: docs/process_traces/2026-08-20-go-session/
(the ONE home for this session's rulings). Gate 1: the canonical
residue was fixed at 60ddb03 through a two-refuter gauntlet (the
execution-lens REFUTED verdict was adjudicated non-defect on the
contract lens's executed evidence; real C1 finding registered as
kernel row RECEIPT-HISTSEM-01), then canonical FULL GREEN at d33f34f
(3,760 ran, 0 failures). Gate 3: D-144 seat pass GO from both seats
(terra xhigh + Opus), zero blockers; post-debate should-fixes queued
as D144-SEATPASS-FOLLOWUPS (SF-1's one-line fix was executably refuted
as a false-refusal hazard — the non-gating report channel is the ruled
shape).

**D-148.5 REGISTRY COUNCIL IS FINAL** (MAGISTRATE-RULING.md + -r2 +
-r3 + cold-delta-verdicts.md in the session custody): enumeration A;
INSTALL DEFERRED TO THE `_v4` FAMILY BOUNDARY (byte-pin blocker +
V1_GRANDFATHERING + the fuse — three independent closures); six
values ruled (r3's B-sections are the operative bytes/tokens); the
`_v4` transaction contract carries the Ed publication gate, envelope
arithmetic, mechanical halt trigger, and BIG classification. The cold
gauntlet ran three rounds (cold Fable + Opus refuter, split verdicts
synthesized each round) and ended FINAL-RATIFY.

**THE `_v3` FUSE LAPSED BY RULING:** arm-evidence expiry ~17:00Z
2026-08-20 (lead-verified); no window race against a closed
WINDOW-COUNCIL-GATE; the `_v4` re-freeze is compelled by executed code
mechanics regardless (idempotent freeze replay + directory-name
generation parsing — see r3 A-4). Windows resume on `_v4` after the
READY sitting and the `_v4` transaction.

**IN FLIGHT AT CHECKPOINT (all read-only seats):** the READY-candidate
council sitting — 12 seats over the prep-sprint packet (L1-L11 +
program rows; 9 terra/codex + 3 Opus), attaching to head 5bd7acf
(P-13 cured by the merge) — and the `_v4` transaction plan co-design
pair (Sol xhigh + Opus, blind). Results land in
scratchpad/ready-sitting/ + v4plan/, then custody.

**ED PACKET (CONSOLIDATED r5 — supersedes the T17 list; the ONE
list; full text in docs/process_traces/2026-08-20-go-session/
rulings-r5-consolidation.md §V-7):**
1. **MINT LICENSE — BLOCKS S-0, the gate on the whole `_v4`
   transaction.** Install the settings rule for the six `_v4`
   freeze/projection commands scoped to the measurement checkout
   (D-148.1: your hands only; the classifier forbids self-granting).
   EVERYTHING WAITS ON THIS.
2. HORIZON 168h for the ten generic freeze-time evidence kinds
   (full three-detector freshness disclosure + idle-cost + the
   D-139-A3 class distinction in the ruling; transaction unmintable
   without a ruled number).
3. V6 marker option (a) build-at-boundary [recommended] / (b)
   UNBUILT token — transaction-blocking.
4. B-δ: windows currently REQUIRE your hands at every T-0
   (CLOCK_ATTESTATION is operator-attestation by construction) —
   choose attended-T-0 for the `_v4` campaign, or authorize the
   D-127 scope + code change as its own work order.
5. NO-REBOOT commitment for the campaign span + pinned boot UUID.
6. ED-QUAL-L6-1 re-scope + T0 reclassification; ED-L10-1 scope
   ruling.
7. Origin-main push freeze during the transaction span (all your
   machines/sessions; suspends the push-promptly habit for the span
   via the stop-card).
8. The sitting's Ed-hands rows E-1..E-11 (E-1 downgraded to
   observability; E-11 the pre-fuse harvest expires ~09:51 PDT
   today).
9. H-6 adoption visibility: the rule-11 packet-finalization gate is
   homed in the charter + validate_gate_packet.py (decision-log
   entry to follow; faithful transcription only).
10. Step-6 exact-byte + terminal-review scheduling — your two
    in-fuse touchpoints, timed at your convenience post-license.

**Session hygiene (additions):** custody staging lives OUTSIDE the
canonical-runner worktree (violated twice this session — cost one
discarded ~25-min run; fix: scratchpad/custody-staging/ pattern, land
between suite runs); the codex wrapper requires the literal
WRITE_SCOPE: line in the prompt when --write-scope is passed; the
`&`-fanout ban caught once (killed before any orphan).

**STANDING HAZARD — the four r6-pinned estimator sources are FROZEN
SURFACES:** `joulewise/powermetrics_fiducial.py`,
`joulewise/uncertainty_evidence.py`,
`joulewise/adapters/powermetrics.py`, `joulewise/reduce.py`
(estimator_code_sha256,
configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:40-43).
ANY byte change invalidates the live acceptance and requires a
science-neutral D-079 reissue at a family boundary. EVERY
WRITE_SCOPE authorization checks this list first (a 2026-08-20 brief
authorized adapters/powermetrics.py for the PROC-TEARDOWN work and
was caught only by repo-wide discovery — the work was remanded to a
new unpinned module).

**TRIGGER SEMANTICS (supersedes T14-GO's loop-line trigger):** Ed starts a
FRESH SESSION at ~23:34 PST pointed at this file. THAT SESSION HAS THE
GO — full fresh Fable + Codex accounts, LIBERAL model use across
terra/luna/Sol/Opus/Fable per the standing fan-out order. It fans out
immediately; the /loop line (T14-GO) is the recommended self-driving
harness once running. Nothing is in flight now; nothing self-starts
before that session.

**GATE SCOREBOARD (four gates to the merge wave, then the T14-GO
sequence):**
1. Canonical FULL GREEN — ONE residue: 3 fails, one root
   (test_unedited_v2_generators_emit_v3_successors × 3 families) — the
   pre-mint successor-emission test vs the now-frozen `_v3` receipts;
   details + log in the T12/T13 run-report addendum. FIX FIRST (small,
   gauntleted), then rerun canonical (~47 min).
2. Fresh-pass — SATISFIED (CLEAN through b92b43d; report + fixed
   findings in custody; post-b92b43d commits are custody landings +
   bookkeeping, focused-verified).
3. D-144 seat pass — packet READY:
   docs/process_traces/2026-08-19-r1-r2-codesign/16-d144-seatpass-packet.md
   (terra xhigh + Opus, debate, Fable ruling).
4. Merge wave under D-148.2 when 1-3 green: impl/r2-s0-mint-resolver →
   integration/phase2-transaction → main.

**READY-MADE PACKETS (all in custody under
docs/process_traces/2026-08-19-prep-sprint/):**
- ready-packet/ — the full READY-candidate council sitting packet (11
  seat rows, 14 program rows, charter brief, 17 OPEN-ITEMS; note the
  dual-assembly reconciliation and the ED-row roll-up 3 closed / 12
  partial / 8 open). The sitting is SUBSTANTIVE — expect STILL-OPEN rows
  and conditions, and the packet's P-13 (head identity) is cured by the
  merge wave FIRST.
- registry-packet/ — the D-148.5 council packet PLUS the executed
  byte-pin experiment: **CONFIRMED-BLOCKER** (install breaks the frozen
  family; no supersession path; windows UNAFFECTED under unchanged v1;
  recommended disposition to rule: defer install to the `_v4` family
  boundary — magistrate + cold instance per rule 11).
- paper-staging/ — registry audit (0/34 locators clean; 8-slot coverage
  hole; era-codes renderer gap F1 = named work item), refreshed-registry
  DRAFT (adoption is a reviewed step), 5 STOP_FILL figure skeletons.
- merge-freshpass.md — gate 2 report.

**ED-DECISION ITEMS the fresh session should surface at the right
moments (not blockers tonight):** (1) sudoers one-liner adding
`-getusingnetworktime` — required before any D-149 auto-GO window (the
T-0 author currently demands an interactive paste; collision documented
in ready-packet ED rows); (2) A4 markers + env-fingerprint semantics
(batch packet); (3) day-5 exact-byte confirmations.

**RECOVERED WORK LEDGER (queue these into the plan):** Phase-3 manifest
supersession (never executed; validator refuses all pack manifests incl.
_v3 — design custodied in the phase2-plan consult); dress rehearsal
ED-Q-L8-2 (never ran; mechanism _v2-stale); WO-CENSUS-SEMANTICS cascade
(ED-Q-L9-3 fixture uncommitted); prewindow_check.sh census patterns;
window.env/capture_t0_step key-set defect; runbook _v2→_v3 pass;
generator CURRENT_FROZEN_RECEIPT constants post-mint; era-codes →
results-renderer closed set; ED-L10-1 re-scope; charter re-baseline +
amendments; the D-149 automation seat-audit the packet demands.

**Session hygiene notes for the successor:** run tests THEN commit —
never in one compound (this session pushed 2 reds that way); packet
assemblers get the CURRENT head pinned at spawn; killed parents can
leave running children (dual-assembly happened — reconcile, don't
clobber).

## ▶▶ T15-PREP (2026-08-19 night) — ACTIVE NOW: 5-HOUR CLAUDE-SIDE PREP SPRINT; CODEX RESETS 23:34 PST (11:34 PM) WITH FULL ACCOUNTS

**Ed's plan (this block + T14-GO below = the complete grasp):** the
pre-/clear session works the PREP LIST below NOW with ample Claude/Fable
capacity; at **23:34 PST the Codex pool resets and Ed is providing a FULL
Fable account AND a FULL Codex account** for maximal fan-out. The prep
exists so the Codex seats (terra xhigh / luna max / Sol) wake into
READY-MADE packets — zero cold starts. After prep is checkpointed, Ed
/clears (possibly twice, with side questions between) and types the
T14-GO /loop line; the five-day run proceeds per T14-GO's sequence.

**PREP LIST (work down in order; 1+2 are merge gates in their own right):**
1. Full canonical at the merge head — machine time; a gate input DONE
   when green. [launched from the pre-/clear session]
2. Fresh-pass review of d59d36f..HEAD (brief in T13-STOP/T13) — Opus
   seat; second gate input DONE when clean. [launched]
3. D-144 pre-merge seat-pass PACKET: scoped S0–S5 artifact diff, brief,
   debate agenda, the D-146/D-147 clauses it verifies — assembled so the
   terra+Opus debate fires at pool return. [assembling]
4. Registry-values council PACKET (D-148.5): the five reserved values —
   three proposed (= the three _v3 pack ids for successor_pack_ids) —
   the remaining two enumerated FROM the R1-registry consult custody
   (docs/process_traces/2026-08-16-grant-identity-consult/ is NOT it —
   find the registry consult under the 2026-08-15/16 traces; the ed
   packet lists the five); seat briefs written. [assembling]
5. READY-candidate council PACKET: evidence rows against the 2026-08-15
   NOT-READY charter form (docs/process/instrument-readiness-audit-
   charter.md, verdict-form amendments 11-12), item by item with custody
   pointers. The heaviest and highest-value prep item.
6. D-149 GO-receipt tooling: the five GO conditions as a mechanical
   checklist evaluation (script + receipt template) so every window GO
   is a written receipt from the first shakedown; pre-stage shakedown
   run cards + window drivers from the T11 working-notes patterns.
7. Paper staging: verify every results-fill-registry row is
   renderable-shaped; number-free figure skeletons per
   docs/paper/figures-plan.md (D-119 disclosure lines verbatim).

**Assembler discipline:** packet assemblers run read-only and write to
session scratch; the LEAD lands their outputs into
docs/process_traces/... serially (one writer per tree). Prep outputs are
committed and pushed as they land so the post-/clear thread inherits
everything through git, never through a dead scratchpad.

**At 23:34 PST:** (GATE COUNT, canonical formulation: FOUR pre-merge gates — canonical FULL GREEN, fresh-pass clean, D-144 seat pass, then the wave itself under D-148.2.) Fan out per the standing order — D-144 seat pass and
registry council first (packets 3+4), gauntlet seats on their outputs,
then the merge wave when all four gates are green (T14-GO item 1), then
straight down the T14-GO sequence.

## ▶▶ T14-GO (2026-08-19 night, FINAL pre-/clear checkpoint) — ED'S FIVE-DAY GO IS ISSUED; THE /loop INVOCATION IS THE TRIGGER

Ed's plan, verbatim intent: gates cleared → this checkpoint → /clear →
the fresh thread FANS OUT and works a FIVE-DAY LOOP on the paper
pipeline. **The GO is granted here.** A fresh session that arrives via
the /loop line below does NOT wait for further permission — it reads
this file and starts. (A fresh session arriving WITHOUT the loop — plain
conversation — still treats Ed's messages as the driver.)

**The loop line Ed will type:**
`/loop work the paper pipeline: read RUN_STATE, continue per the standing orders (D-128 mandate, D-148 gate-authorized merges, D-149 window automation); never idle between blocks`
Self-paced dynamic mode: match each wakeup to what is actually awaited
(suite ~50 min; overnight window = hours; desk blocks 20–30 min).

**Cleared gates (all durable):** permission allowlist live in
.claude/settings.local.json (project scripts both interpreters, the
measurement checkout incl. its git, caffeinate, unittest); D-148.2
merges gate-authorized; D-148.4+D-149 full no-hands window automation
with the five-condition auto-GO (each GO a receipt in window custody);
D-148.5 registry values to council. Ed's only retained items: hands-on
hardware, reboots, new sudo, claim publication, exact-byte confirmation
— batch to ONE day-5 packet unless truly blocking.

**FIVE-DAY SEQUENCE (fan out maximally per the standing fan-out order;
Codex pool resets ~23:22 nightly — terra xhigh / luna max seats, Opus
corps when the pool is dry):**
1. Merge gates: rerun full canonical at the merge head; rerun the
   fresh-pass over d59d36f..HEAD (brief in the T13 block); run the
   D-144 BIG-design pre-merge seat pass (terra+Opus debate over the
   implemented S0–S5 artifact, Fable ruling). All green → MERGE WAVE
   impl/r2-s0-mint-resolver → integration/phase2-transaction → main.
2. Registry council (D-148.5): five reserved values (three proposed =
   the _v3 pack ids) → install the row registry (kernel-transaction
   discipline).
3. READY-candidate council: assemble the packet against the 2026-08-15
   NOT-READY charter form; clear WINDOW-COUNCIL-GATE.
4. Windows under D-149, shakedown FIRST (D-139): instrument-verification
   captures, then alpha (1p5b floors), beta (7b floors), gamma
   (contrast) overnight; every GO receipt custodied; D-078 no-retry.
5. Reductions → verdicts → floors from issued artifacts → paper §6
   tables filled ONLY from the results-fill registry → figures per the
   registered plan with D-119 disclosure lines verbatim → full-draft
   fidelity + pedagogy passes (the writing standard binds) → day-5
   packet to Ed (tables, receipts, refusal log, exact-byte
   confirmation).

**Standing discipline (the short list the loop must never drop):** stop
means stop; refused captures end lanes (diagnose, never re-arm-and-hope);
two same-signature failures → consult, not round three; quiet blocks =
zero tool calls mid-capture; one writer per worktree; the lead verifies
receipts itself; kernel edits = kernel+regen+pins one transaction;
explainer prose obeys the global writing standard; keep the remote
current; count Codex runs (ledger blind).

**Where everything is:** T13/T13-STOP (directly below) = gate-input
status and the fresh-pass brief; T12-FINAL = the executed-transaction map
and custody index; docs/process/ed-s5-mint-decision-2026-08-19.md = the
completed confirmation table awaiting Ed's byte confirmation (day-5
packet item); decision log D-144..D-149 = tonight's authority set.

## ▶▶ T13-STOP (2026-08-19 night, Ed stop orders ×2) — NOTHING IN FLIGHT; RESUME ONLY ON ED'S EXPLICIT GO (SUPERSEDED same night: Ed resumed prep — see T15-PREP above; the go-for-pipeline semantics of T14-GO stand)

*(Second stop, later the same night: after the stop below, Ed cleared
gates — the permission allowlist is live in settings.local.json and
D-149 standing window automation is minted/pushed — and the gate-input
reruns were briefly restarted, then Ed ordered a full stop again. Both
were killed early; the gate-input status below is unchanged: ALL
UNSATISFIED, rerun from scratch. The successor does NOT self-start the
pipeline: gates are cleared, but the run begins on Ed's explicit go.)*

All background work stopped cleanly (the final-canonical run and the
fresh-pass reviewer were killed mid-run — BOTH GATE INPUTS ARE
UNSATISFIED and must be rerun from scratch). S5 is COMPLETE and landed
(freeze-0003 ×3 verified; confirmation table filled; branch pushed @
75cb868 incl. the S6 bookkeeping: kernel transaction green, T12/T13 run
report, README blurb). NO MERGE HAS OCCURRED.

**The complete pre-merge gate list for the successor (corrected — Ed
caught the omission):**
1. Final canonical FULL GREEN at the merge head (rerun; ~46 min).
2. Fresh-pass review over d59d36f..<the merge head> — SATISFIED
   2026-08-19 night: CLEAN through b92b43d, all claim-bearing digests
   recomputed and matched (report:
   docs/process_traces/2026-08-19-prep-sprint/merge-freshpass.md);
   commits after b92b43d are the fix-round of that report's own
   bookkeeping findings + prep landings and carry no pack/receipt bytes.
3. **The D-144 BIG-design pre-merge seat pass** — terra+Opus debate over
   the implemented S0–S5 artifact, Fable ruling on findings.
   POOL-GATED (~23:22). This is a ruled requirement of D-146/D-147's own
   classification, not optional.
4. Then the merge wave under D-148.2 (gate-authorized; no Ed wait).

Also queued at pool-return: the D-148.5 council pass on the five R1
row-registry reserved values. The run report's canonical addendum is
still a placeholder — fill it from gate input 1.

## ▶▶ T13 CHECKPOINT (2026-08-19 late evening) — CLEARED-CONTEXT RESUME POINT; READ THIS BLOCK THEN docs/process/ed-s5-mint-decision-2026-08-19.md

**Ed ruled seven decisions in-session — ALL RECORDED as D-148** (decision
log index + body; memories updated: merge-authority, ed-hardware). The
operative ones for a fresh session:

- **S5 mints:** Ed chose the settings-rule route (D-148.1), but the
  classifier also blocks Claude from WRITING the rule — it needs ED'S
  HANDS (30 s; exact snippet now at the top of the S5 packet). Once the
  rule exists: run the six commands (U11 projection ×3 then freeze-0003
  ×3, ONE AT A TIME, commit per step, D-078 no-retry on any refusal) at
  /Users/edr/JouleWise-measurement-20260818 (branch checked out there,
  ahead-synced through S4 @ 3a75a770 + landed on origin), then verify
  receipts (path-binding to the measurement checkout, status PASS,
  receipt_id freeze-0003, predecessor triple matching the packet's
  freeze-0002 shas), then land by `git pull --ff-only
  file:///Users/edr/JouleWise-measurement-20260818 impl/r2-s0-mint-resolver`
  from a dev worktree (NEVER push from the measurement checkout), then
  fill the packet's three [PENDING MINT] confirmation rows. HARD
  DEADLINES: evidence dies ~2026-08-20T16:51Z or on ANY REBOOT.
- **Merges (D-148.2):** gate-authorized. When the S6 gate shape is green
  (review of final head + CI + fresh pass over post-review commits),
  merge impl→integration/phase2-transaction→main WITHOUT waiting for Ed.
- **Quiet windows (D-148.4):** lead-delegated whenever no hands are
  needed at the machine — schedule and run at lead discretion. Hands/
  sudo/reboots stay Ed's.
- **R1 registry values (D-148.5):** Ed defers to council — run the
  co-design/council pass (Codex pool returns ~23:22 tonight; terra/luna
  seats per the roster in T11) over the five reserved values (three
  proposed = the `_v3` pack ids), then install the row registry (queued
  kernel row, kernel-transaction discipline).
- **Limitations (D-148.6/.7):** the in-process-adversary family and the
  748-bundle anchor-v2 population are ACCEPTED/REGISTERED — recorded in
  CLAIMS_STATUS.md; fold into the paper's §7 at the next docs touch (the
  anchor-v2 paragraph already exists there; add the registered status).

**AFTER S5, the remaining close (S6) is:** kernel rows (state_kernel
M7/M8 + transaction row — consistency-sweep findings in
docs/process_traces/2026-08-19-refreeze-execution/reports/consistency-sweep.md)
→ T12/T13 run report (docs/run_reports/) → final canonical FULL GREEN at
the closed head → README activity blurb → gate shape → MERGE WAVE
(pre-authorized). Then: council on registry values; the profiler pilot +
first v3 quiet windows under D-148.4; Ed-owed residue (family marker
retrofit, A4 markers, env-fingerprint semantics — batch packet).

**Everything else about this session** (what S0–S4 are, custody layout,
the guide/paper rewrite + writing standard, discipline notes) is in the
T12-FINAL block directly below — read it next.

## ▶▶ T12-FINAL CHECKPOINT (2026-08-19 evening; Codex pool EXHAUSTED until ~23:22 local) — SUCCESSOR STARTS HERE

**THE TWO CLOCKS THAT MATTER:**
1. **S5 freeze mints are Ed-gated** (classifier block; packet
   `docs/process/ed-s5-mint-decision-2026-08-19.md` has the three options
   and exact commands). The S4 evidence EXPIRES ~2026-08-20T16:51Z and
   DIES ON ANY REBOOT (boot session da90818c…). **NO REBOOTS** until the
   mints land or Ed chooses re-authoring.
2. **Codex (terra/luna/Sol) usage exhausted until ~23:22 tonight.** Nothing
   in the remaining transaction needs Codex (S5 = Ed + lead; S6 = lead +
   Opus seats); future gauntlet rounds do.

**STATE (branch impl/r2-s0-mint-resolver, everything pushed):** the D-147
transaction is EXECUTED THROUGH S4 — S0 resolver / S1 anchor-v3 capture
flip + p2-038.3 era system + claim barrier + D-079 r5→r6 (both
neutrality-proven 19/19, r6 live, sha 0227bca3…) / S2 goldens (mint suite
FULL GREEN) / S3 `_v3` family emitted bound-to-r6-at-birth / S4 evidence
33/33 PASS authored at the measurement checkout (its git state: branch
checked out, S4 commit landed to origin via pull). Canonical at the
S1-clean head: 3,755 ran, docs-freshness-only red (now cured by the
README fix). Full execution custody (lens reports, delta audits, fix
reports, r5/r6 issuance + neutrality proofs, S4 manifest, suite logs):
`docs/process_traces/2026-08-19-refreeze-execution/`. Rulings + co-design
corpus + r6 amendment: `docs/process_traces/2026-08-19-r1-r2-codesign/`.

**DOCS (Ed-driven, advisor-facing):** instrument guide fully rewritten to
Ed's writing standard (global CLAUDE.md §Writing standard; memory
`explainer-docs-plain-language-debt` — READ BOTH before writing ANY
explainer prose); paper enriched + plain-language pass; the pulse-fit
worked-example page is committed at
`docs/guides/figures/pulse-example.html` and published at
https://claude.ai/code/artifact/08ae099a-5dd1-409e-a88e-257ffb3697cf.
Guide+paper are synced to main (docs-ahead-of-code, noted in the commits).

**SUCCESSOR ORDER:**
1. If Ed has ruled on S5: execute per the packet (U11 projection ×3 →
   freeze-0003 ×3 at /Users/edr/JouleWise-measurement-20260818, one commit
   per step, NO retries on refusals) → land via pull-from-measurement-
   checkout → lead verifies every receipt (path-binding, PASS, ordinal
   0003, predecessor triple vs the T10 table) → fill the confirmation
   table's three [PENDING MINT] rows.
2. S6 close: kernel rows under kernel-transaction discipline
   (state_kernel M7/M8 from the consistency sweep + a transaction row);
   T12 run report (docs/run_reports/, records the mint outcome); final
   canonical FULL GREEN at the closed head; README activity blurb; then
   the merge path (impl/r2-s0-mint-resolver → integration/phase2-
   transaction → main per rule-4/D-072 gates).
3. Ed-owed beyond S5: family marker (recommend: retrofit co-design),
   R1 row-registry reserved values (3/5 supplied = the `_v3` ids), A4
   markers, env-fingerprint semantics, anchor-v2 population disposition
   (recommend the registered-limitation paragraph), exact-byte
   confirmation.

**Worktrees:** this session's scratchpad (cbd9b7b5…) dies with it — all
load-bearing content is now committed; wtS0 (branch), wtTXN, wtCANON,
wtDOCS and the lens/delta trees are disposable. The measurement checkout
is AHEAD-synced (S4 landed) and must not be reset.

**Discipline notes (session additions):** never `| tail` a discriminating
suite run (bitten again this session — full log to a file, then grep);
implementation codex runs need `-s workspace-write` and prompt WRITE_SCOPE
as inline JSON; linked-worktree git metadata is outside codex sandboxes —
the lead commits; glossing passes cluster their factual errors in the NEW
glosses — fidelity-check those specifically.

## ▶▶ T12b (2026-08-19 midday) — TRANSACTION EXECUTED THROUGH S4; S5 MINTS BLOCKED ON A PERMISSION RULING (ED)

READ FIRST: docs/process/ed-s5-mint-decision-2026-08-19.md — the ONE
blocking decision (classifier blocks the mint scripts; three options; the
S4 evidence expires ~2026-08-20T16:51Z and DIES ON REBOOT).

State on impl/r2-s0-mint-resolver @ 3a75a77 (pushed): S0 resolver + S1
capture flip (p2-038.3, claim barrier, D-079 r5→r6 chain, both
neutrality-proven 19/19) + S2 goldens (mint suite FULL GREEN, first of the
cycle) + S3 _v3 family emission (bound r6 at birth; _v1/_v2 byte-preserved)
+ S4 evidence ×3 (33 receipts PASS at the measurement checkout, landed) —
each stage through the C-028 gauntlet (two-lens reviews, fix rounds with
delta re-audits, magistrate final reviews; custody
docs/process_traces/2026-08-19-r1-r2-codesign/ + session scratchpad
r5-issuance/, r6-issuance/, s2-goldens/, s4/). Canonical at the S1-clean
head: 3,755 ran; residual reds now only docs-freshness (S6) after the
three-window fixture fix + residue round; the evidence-author pair cured
at S3. Remaining: S5 freeze-0003 ×3 (BLOCKED on Ed; procedure + exact
commands in the packet) → S6 docs/canonical FULL GREEN → the r6
confirmation table (draft in the packet, three [PENDING MINT] rows).

## ▶▶ T12 (2026-08-19) — R1/R2 CO-DESIGN RULINGS RATIFIED; CYCLE RESUMES UNDER THEM

*(Superseded detail: this block's r5 references predate the r6 reissue —
the live generation is r6; see T12b above and
`docs/process_traces/2026-08-19-r1-r2-codesign/15-amendment-r6.md`.)*

The two rulings that parked the re-freeze cycle at steps 3-6 are RATIFIED
under the co-design protocol (now minted D-144; first application, protocol
validated — both debates produced executed refutations of seat positions
and of the magistrate's briefs). Custody:
`docs/process_traces/2026-08-19-r1-r2-codesign/` (14 files, reading order).
Rulings: D-146 (R1, `13-r1-ruling.md`) and D-147 (R2, `14-r2-ruling.md`);
generation record + t-quantile note minted D-145.

**What changed vs the parked brief:** (1) the flip mandates a
science-neutral D-079 r5 in the SAME COMMIT (r4 pins the adapter bytes);
(2) the `_v3` family binds r5 AT BIRTH (the emission-time file-sha pin
would not catch a later retarget); (3) parked step 6 is AMENDED —
freeze-0003 mints on the NEW `_v3` roots, chained to the untouched `_v2`
freeze-0002 receipts; no freeze-0002 re-mint anywhere; (4) the `_v2`
generators are frozen pack content and are READ-ONLY — `_v3` is emitted by
the unedited generators then draft-retargeted; (5) the canonical red
`embeds_allowance_once` roots in the shared test helper (executed proof),
fixed BEFORE the flip; (6) a mechanical claim barrier (one shared
predicate, new engine reason `capture_pipeline_superseded`) is part of the
flip — no such barrier exists today (executed: all 769 window summaries
pass the reducer-version barrier).

**Execution order (D-147 S8, binding):** S0 R2 kernel (resolver/rewiring/
schema/genesis rename) → S1 R1 flip + r5 (one commit) → S2 goldens once →
S3 `_v3` emission + retarget + checks → S4 evidence re-author ×3 → S5
freeze-0003 ×3 (LAST acceptance-bearing step, at
/Users/edr/JouleWise-measurement-20260818) → S6 docs → canonical FULL
GREEN → Ed's v3 confirmation table (now carries r5 identities).
Implementation runs the full C-028 gauntlet per stage; Fable final review;
one more two-seat pass over the implemented artifact pre-merge (BIG).

**Ed-owed (delta from T11 list):** the confirmation table basis moves
r4 → r5; family-marker ruling recommendation = `_v3` lands first, marker
retrofits via its own co-design pass; R2 supplies three of the five R1
row-registry reserved values (`successor_pack_ids` = the `_v3` ids);
stored-anchor-v2 population disposition (registered limitation vs barrier
alone — magistrate recommends the limitation paragraph).

## ▶▶ T11 CHECKPOINT (2026-08-18 late evening — Ed-ordered session checkpoint; SUCCESSOR STARTS HERE)

**Ed's directive at checkpoint:** fresh session, point at RUN_STATE. Roster:
sparing Sol; Fable+Opus liberally; terra xhigh / luna max as Codex seats;
watch the Codex pool (ledger blind — count runs). CO-DESIGN RULE (D-144
pending mint): independent Sol(or terra)+Opus designs → bounded debate →
Fable ruling → gauntlet → Fable final review; big designs get one more
debate pass post-review.

**State:** everything through the anchor-v3 arc is committed/pushed on
`integration/phase2-transaction`. Read IN ORDER: (1)
docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md — the
full two-day trace; (2) docs/process_traces/2026-08-18-anchor-v3-science-review/
— the ratified science; (3) the morning packet + ed-confirmation docs.
Day-2 arc: knife-edge anchor root-caused → anchor-v3 (set-membership,
cold-reviewed, 7 conditions executed) → corpus n=17 r3 issued (screens
TIGHTENED) → capture activation + science-neutral r4 (bb81323) → THE
ATOMIC RE-FREEZE CYCLE WAS MID-EXECUTION at checkpoint (an Opus agent was
executing: fan-out to floor-mint/detection-floor/pack generators →
regenerate 3 _v2 packs → evidence re-author → freeze-0002 re-mints AT
/Users/edr/JouleWise-measurement-20260818 (path-binding!) → canonical
suite → confirmation table to docs/process/ed-confirmation-2026-08-18-v3.md).
CHECK `git log` on the branch: whatever the agent landed is durable;
resume the cycle from its last commit against the brief recorded in
trace-notes.md (§"Conditions executed + budget ruling + generation
launch" and after). Fan-out list: the f4d5ea7/2de24b0 commit messages +
the generation report's enumeration (test_mint_floor_artifact_generalized
must return to full green; canonical FULL GREEN is the bar).

**Then (the night plan Ed licensed):** quiesce fleet → quiet block 1:
v3-native calibration captures (update the shakedown clone
/Users/edr/JouleWise-window-custody/shakedown-20260818/clone to the final
head first; driver + pristine-ledger pattern in the working-notes dir) →
quiet block 2: the GSM8K profiler pilot (~64 min; branch
pilot/gsm8k-harness @ f0c4399 in the wtS-scout worktree; RUN_CARD in
docs/process_traces/2026-08-18-gsm8k-profiler-pilot/; dry-run validated;
lead launches live) → morning reductions + Ed's confirmation.

**Ed-owed rulings (accumulated):** the v3 confirmation table (supersedes
packet §3); family-marker particulars; R1 registry reserved values (five
items); profiler memo open Qs (cap-terminated completions; prompt style);
A4 contrast markers; environment-fingerprint semantics. Decision-log
minting owed: D-144 (co-design rule), the r3/r4 generation entry, the
t-quantile note, the load-sensitive determinism test queue item.

**Worktree map:** wtTXN (scratchpad, branch checked out) — the successor
should create its OWN worktrees; the scratchpad path dies with the old
session but all content is committed. Measurement checkout =
/Users/edr/JouleWise-measurement-20260818 (freeze mints live HERE).
Custody: ~/JouleWise-window-custody/{shakedown-20260818,ed-qual-20260817,
profiler-pilot-20260818}. The stale cs-pedagogy worktree removal is
classifier-blocked — Ed can `git worktree remove --force` it.

**Discipline notes for the successor:** one writer per worktree (wrapper
rc75 lock enforces); never launch scoped codex runs into a tree with ANY
other writer including yourself; agents must not launch Sol; quiet blocks
mean ZERO tool calls mid-capture; pipe-masking on discriminating runs is
forbidden; the D-078 no-retry discipline covers every refused capture.

## ▶▶ T12 POINTER (2026-08-19 evening) — ACTIVE WORK IS ON `impl/r2-s0-mint-resolver`

The live successor order is the T12-FINAL CHECKPOINT in RUN_STATE.md **on
branch `impl/r2-s0-mint-resolver`** (pushed; it carries the executed D-147
transaction S0–S4, the S5 Ed-gate + evidence deadline — NO REBOOTS — and
the S6 close order). That branch supersedes the older T11 pointer to
`integration/phase2-transaction` for active work; the integration branch
is the merge target, not the work site. Main carries the enriched
guide/paper docs ahead of the code they describe (noted in those commits).

## ▶▶ T10 CHECKPOINT (2026-08-18) — READ docs/process/ed-morning-packet-2026-08-18.md FIRST

The Phase-2 transaction is EXECUTED to its confirmation head (canonical
3,688 green; family frozen with freeze-0002 chains, live-authenticated at
/Users/edr/JouleWise-measurement-20260818; D-079 r2 issued incl. the D-143
budget correction; first-light shakedown b_fiducial IN-BAND). Ed's morning
packet carries the exact-byte confirmation table and the reserved rulings
(family marker; R1 registry values). Session record:
docs/run_reports/2026-08-18-t10-session.md. This checkpoint supersedes the
branch's earlier stale top (B-2 in the T10 report); main's own T10
checkpoint (62c6a06) is consistent with this one.

## ▶▶ T9 CHECKPOINT (2026-08-16) — PHASE 1 CODE COMPLETE; A NEW SESSION STARTS HERE

**STATE IN ONE BREATH:** T8's successor order is EXECUTED. The Phase-1 CODE
WAVE is merged — all four mergeable work orders are ON MAIN — #153 should-fix batch (8035bf2, final head 24df3df),
#154 T-0 F4 honest contract (a59c795), #155 WO-CONSUMPTION-EDGE (d54db78),
#156 WO-LAUNCH-BINDING stages 1+2 campaign side (f392ff6) — each through the
full C-028 gauntlet + rule-5 final-head passes + a pre-merge integration tree
(all cross-stream seams clean). WO-DETECT-PULSES-BUDGET + the calexits flake
fix are gauntlet-complete and MERGE-STAGED FOR PHASE 2 on
impl/wo-detect-pulses-budget @ 5449e58 (R-t9-4: the branch edits D-079-pinned
estimator inputs; it merges inside the atomic re-freeze that re-issues the
acceptance artifact). WO-L2-REAUDIT is DELIVERED — Coverage VERIFIED
(251/251 independent enumeration; custody
docs/process_traces/2026-08-15-l2-reaudit/). The council's NOT-READY verdict
STANDS; nothing was measured or armed. Session record:
docs/run_reports/2026-08-16-t9-session.md (the ONE home for the arc,
catches, rulings R-t9-1..7, and the launch-binding F3 cold-gate story —
custody docs/process_traces/2026-08-16-launch-f3-coldgate/, self-contained).

**SUCCESSOR ORDER:**
1. **Phase-1 residue:** WO-CENSUS-SEMANTICS stays HARD-gated on ED-Q-L9-3.
   Launch-binding: stage 3 MERGED #157 (bd333de); calibration-side stage 2
   DONE on the staged branch @ e22e658 (delta-ACCEPTED at the synced head);
   only stage 4 (successor flag) remains, inside the Phase-2 transaction —
   whose full plan is custodied (2026-08-16-phase2-plan-consult). WO-RECORDER-GRANT-IDENTITY (own cold gate) and
   WO-PROOF-RUNNABILITY-REPAIR (proof-semantics trust gauntlet; restores the
   proof-matrix automatic triggers) are queued kernel rows.
2. **Phase-2 PREP is the successor session's OPENING PROGRAM** — the plan
   consult's F4 list (docs/process_traces/2026-08-16-phase2-plan-consult/,
   consult.md §F4) enumerates what is preparable BEFORE Ed's GO: D-079
   reissue tooling + corpus authentication (off the staged head e22e658 —
   F3's stop-condition binds: any change to the accepted 19-member set is a
   cold review, not a pin refresh), R1 schema/tooling/refusal implementation,
   AXI descriptor + release-gate tests, merge simulation, generator repairs +
   successor templates, dry-run roots + packet templates. Calibration
   stage-2 (the first F4 item) is DONE + delta-ACCEPTED this session.
   Deliberately HELD at T9 close (deep-context magistrate; claim-adjacent
   material deserves fresh context — the motion-vs-progress rule applied to
   the lead itself).
3. **Phase 2 EXECUTION (the ruled order, council-verdict.md):** ONE atomic
   successor-family re-freeze, LAST — folds the D-079 acceptance re-issue
   (unblocks merging impl/wo-detect-pulses-budget), M-2 retirement, the
   ALPHA/BETA --plan reconciliation, launch_lineage_required successor flag.
   Then Phase 3 manifest SUPERSESSION + focused re-audit w/ adversarial
   coverage re-enumeration; Phase 4 READY-candidate sitting, fresh cold pair.
4. **ED-OWED — A1/A2/A3-defaults RULED 2026-08-17 (D-139): adversary family
   closed, gamma stats adopted (Holm m=2), p256 dedicated floor, Phase-2
   defaults approved, SHAKEDOWN-FIRST directive (first post-READY quiet
   consumption = minimal instrument-verification runs, claims after).
   REMAINING Ed items: hardware batch B, A4 marker ruling, environment-
   fingerprint semantics, final exact-byte publication confirmation.** Packet:
   docs/process/ed-batch-packet.md. Otherwise unchanged from T8 (qualification script, dress
   rehearsal, sampler checklist, rail probe, backlight rows, ED-Q-L9-3
   EARLY, a9/a10 desk replay, ED-QUAL-L4-1) PLUS the three risk-appetite
   calls now explicitly ONE FAMILY (recorder race, T-0 capture provenance,
   hostile same-UID injection — the launch-consumption forged-context
   limitation joined it this session) and the contrast-pack
   pending-ratification ruling. The WO-CONSUMPTION-EDGE scientific rulings
   (prefill test/direction, multiplicity family/m, p256 floor-or-transport,
   production freeze + production-pack L10 replay) are RULING-REQUIRED
   before gamma's edge can close.
5. **Desk debt:** none carried — T9 report landed same-session; queue/kernel
   closures and the consistency sweep landed at T9 close (this commit).

**Standing cautions (T9 additions):** local-date convention bit three times
in one session — date artifacts at write time from `date`, never from memory;
one codex-run per background call (never `&`-fanout); never `| tail` a
discriminating suite run; execution lenses need workspace-write + $TMPDIR;
kernel edits = kernel + regen + test pins, one transaction; anchors cited to
file:line and verified; regression lists attack-shaped.

## ▶▶ T8 FINAL CHECKPOINT (2026-08-15, Ed clear order) (superseded by T9 above; kept as record)

**Nothing in flight.** All Sol runs stopped/harvested, zero live codex
processes, the ancient orphan watcher (pid 29679) killed, the stray
caffeinate gone on its own. Everything load-bearing is pushed (main @ a61ac92). Scratchpad worktrees are disposable (all branches pushed or
deliberately deleted). Session task list is superseded by this block.

**STATE IN ONE BREATH:** the readiness council ruled **NOT-READY 0/11**
(full custody docs/process_traces/2026-08-15-readiness-council/ — read
council-verdict.md FIRST); **Phase 0 is COMPLETE** (R1 content-bound
freeze-evidence lifecycle via cold gate; R2 FROZEN_PLAN; R3 P2-006
retirement; R4 + the remanded M-2 gate — instrument narrowed, scope pinned
to three receipt hashes; six WO contracts adopted; every ruling custodied
under docs/process_traces/2026-08-15-*/); **Phase 1 is 2 MERGED + 1 PR +
1 staged**: #150 kernel (WINDOW-COUNCIL-GATE LIVE on main — no quiet-mac
selection until a READY-candidate verdict), #151 recorder (close-out
blocker L4-B1 cured; check-to-grant race = REGISTERED LIMITATION,
WO-RECORDER-GRANT-IDENTITY queued for its own gate).

**SUCCESSOR ORDER:**
1. ~~PR #152~~ **MERGED at checkpoint close (a61ac92)** — CI went all-green
   during the checkpoint; D-121 verified (head 9e8936a unchanged) and
   merged. ALL THREE built Phase-1 streams are now ON MAIN: #150 kernel
   gate, #151 recorder, #152 T-0 producer.
2. **WO-CONSUMPTION-EDGE: relaunch FRESH — the successor's FIRST action** (nothing lost — the in-flight
   build was stopped ~20 min in per the T7 precedent). Contract = the
   decision-log "WO-CONSUMPTION-EDGE contract ADOPTED" entry + the ONE
   home docs/process_traces/2026-08-15-consumption-edge-consult/. Fresh
   worktree + branch impl/wo-consumption-edge off current main; Sol xhigh,
   workspace-write, WRITE_SCOPE from the contract entry; then C-028
   gauntlet.
3. **WO-LAUNCH-BINDING stage 2+**: branch impl/wo-launch-binding @
   345bfbb is a WIP CHECKPOINT (launcher core + verify_consumed_launch +
   3 downstream gates, focused-green; does NOT yet cure L8-B7 — launch
   stays NO-GO). The F2 lineage-locator mechanism is ADOPTED (decision
   log + docs/process_traces/2026-08-15-launch-lineage-consult/): stages
   1-4 enumerated there; stage 4 is Phase 2. Continue with stage 1
   completion (retire public consume) + stage 2 (writer-side 8-point
   auth) on that branch.
4. **Remaining Phase-1 launches:** WO-DETECT-PULSES-BUDGET (carry the
   singlelens refuter's L2-1 remedy correction: deterministic budget +
   anchor-unresolved bypass), WO-L2-REAUDIT (251-test universe),
   WO-CENSUS-SEMANTICS (HARD-gated on ED-Q-L9-3 — needs Ed),
   should-fix batch (sweep B1 alpha_arm_readiness re-anchor, B2/B3 queue
   closures + D-130 disposition, B6 README, B7 paper floor-regime row
   [P1 claim-bearing], L11's three paper corrections, and
   FLAKE-CALEXITS-311-REDERIVE — the flake cost another CI rerun today;
   implement its registered fix shape). T-0 F4 honest-contract deltas
   (correct the D-134 cl.6 overclaim + remove the injection seam) fold
   into a follow-up on the t0-producer lane after #152 merges.
5. **Phases 2-4** per council-verdict.md: successor-family re-freeze
   (R1-ruled route, ONCE, atomically, LAST — folds M-2 retirement, the
   ALPHA/BETA plan-path + --plan reconciliation, launch_lineage_required)
   → baseline-manifest SUPERSESSION (+pack_digest_algorithm + chain-
   template note) → focused re-audit w/ adversarial coverage
   re-enumeration → READY-candidate sitting, fresh cold pairing.
6. **Desk debt owed:** T8 run report + C-058 ADDENDUM (the record after
   the council verdict: Phase 0 rulings, both cold gates incl. the
   recorder-race gate that REJECTED the magistrate's own proposal on
   executed evidence, #150/#151/#152, the wake-source failure class +
   memory rule); consistency sweep over the span; skill-log rows are
   current through today.

**ED-OWED (ONE batched session when Phase 1 nears close; NOTHING now):**
the expanded qualification script (D-127 sudoers install
scripts/joulewise-network-time.sudoers sha 7dfe980b… + exercise both
vectors; dress rehearsal E-4→E-9 + author→arm→verify→consume vs scratch
custody; sampler checklist; rail probe; backlight rows; ED-Q-L9-3
quiet-state baseline — EARLY if any tap happens, it gates the census WO;
a9/a10 desk replay; ED-QUAL-L4-1 decisive replay) PLUS three
risk-appetite/paper-scope calls the gates surfaced: (1) recorder-race
threat model (concurrent local writer in/out of model), (2) T-0 capture
provenance (trusted-operator MVP claim vs option-(a) attested
architecture — Rivoire-bar question, consult custodied), (3) hostile
same-UID mid-window injection (the launch-lineage residual, same family).
Plus the contrast-pack pending-ratification/TODO-markers ruling.

**Standing cautions minted this session (fold at bookkeeping):** never end
a turn with zero live background work (memory: turn-end-wake-source-rule —
two occurrences cost hours); subagent relays wrapping the codex MCP route
wedge silently — lead-shell codex-run-v3 launches, one worktree per run
(per-worktree lock), WRITE_SCOPE must START a line, -C a scratchpad
worktree to dodge the nested-repo refusal; rc-65/thin-report runs often
completed on disk — harvest via git diff + report file before relaunching;
NEEDS_SCOPE is never resumable (fresh continuation run in the same
worktree works); decision-log tail conflicts are append-unions — resolve
by keeping both, guard the heading-glue class; macOS has no `timeout`;
D-121 requires branch head == audited head, verified in the same turn.

## ▶▶ T8 STATE (superseded by FINAL CHECKPOINT above; kept as record) (2026-08-15) — COUNCIL VERDICT: NOT-READY; REPAIR PROGRAM IS THE DESK PROGRAM

**PHASE 1 PROGRESS (latest): PR #150 WO-KERNEL-RECONCILE MERGED (47d2645)
— the WINDOW-COUNCIL-GATE is LIVE on main** (fleet blocker L1-B2 closed:
no quiet-mac window selectable until a READY-candidate council verdict;
P2-006 retired per R3). Phase 0 fully ruled/custodied (R1-R4 + M-2 gate +
6 WO contracts, docs/process_traces/2026-08-15-*/). In flight: PR #151
recorder-authz (cold-gated race → registered limitation; awaiting CI);
WO-T0-PRODUCER (built, 5-blocker review → F1/F2/F3/F5 fix round, F4
capture-provenance → design consult vs the recorder-race precedent).
NEW queued: WO-RECORDER-GRANT-IDENTITY (own gate). RULING-REQUIRED:
contrast-pack pending-ratification/TODO markers (Ed-adjacent); the T-0
capture-provenance disposition (Ed risk-appetite, parallel to the
recorder-race threat-model call).

**THE READINESS COUNCIL RAN IN FULL AND RULED: NOT-READY, 0 READY / 11
NOT-READY.** Full custody (fleet reports, nine refuter verdicts, cold
pairing rulings, verdict): `docs/process_traces/2026-08-15-readiness-council/`
(committed bd7f81c; read council-verdict.md FIRST — it is the operative
instrument). No funded window may be armed. Windows are not scarce (Ed);
the repair program is the program.

**Arc this session:** eleven-seat fleet (11/11, 46.7 min, 2.41M tokens) →
9 Sol xhigh C-028 refuters (5 relay agents wedged ~7h, killed, relaunched
from the lead shell — worktree-per-run; verdicts killed L8-B4 + WO-L2-4 as
phantoms, felled L2's READY, found the doubled plan-path defect + the
terminal-review-trailer gap) → rule-11 cold pairing (cold Fable + Opus
contract refuter; found 4 process blockers in the sitting itself — no
custody, packet gaps, M-2 not adjudicable as submitted, coverage
undischarged — ALL CURED before the verdict was recorded).

**THE WORK-ORDER PROGRAM (4 phases, council-verdict.md §"WORK-ORDER
PROGRAM" is the ONE home — not restated here):** Phase 0 design rulings
(R1 freeze-evidence lifecycle w/ mandatory Sol consult; R2 FROZEN_PLAN;
R3 P2-006 retirement; R4 M-2 execution note + the REMANDED M-2 cold gate;
consults for validator/finalizer + recorder authz) → Phase 1 parallel code
WOs (kernel-reconcile first) → Phase 2 re-freeze ONCE atomically LAST +
successor packet → Phase 3 manifest SUPERSESSION + focused re-audit w/
adversarial coverage re-enumeration → Phase 4 READY-candidate sitting,
fresh cold pairing. Program NOT certified complete (recorded clause).

**PROGRESS SINCE THE VERDICT (same day):** second-lens refuter CLEARED
all four SINGLE-LENS claims (custodied 15d00d2, verdict addendum); C-058
LANDED (af7c23b, index row + entry); R4 M-2 execution note ENTERED
(c0b7068); **R1 CONSULT DELIVERED AND CUSTODIED**
(docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/ — Sol
recommends option C, content-bound durable evidence + freshness-class
taxonomy + family-level successor tool for semantic changes only; the
design amends D-131/D-134/D-137/D-078 ⇒ ADOPTION REQUIRES ITS OWN
RULE-11 COLD GATE, packet = the consult + the A-cluster refuter record).
**Next desk actions:** R1 adoption cold gate → R2 FROZEN_PLAN ruling →
R3 P2-006 ruling → remanded M-2 cold-gate packet w/ primaries → Phase 1
launches (WO-KERNEL-RECONCILE first; multi-stream per the verdict).

**ED-OWED: NOTHING until Phase 1 nears close.** Then ONE batched session
(expanded qualification script): D-127 sudoers install + exercise, dress
rehearsal E-4→E-9 + author→arm→verify→consume vs scratch custody, sampler
checklist, rail probe, backlight rows, ED-Q-L9-3 quiet-state baseline
(EARLY — it gates the census WO; can ride any earlier tap), a9/a10 desk
replay. NO REBOOT still preferred (moot for arming — evidence re-authors
regardless under the ruled lifecycle — but boot-session continuity keeps
the qualification replays cheap).

**Standing cautions minted this session:** refuter relays via subagent
wrap the codex MCP route and can wedge silently — launch >30-min Sol
reviews from the LEAD shell with codex-run-v3, worktree per run (lock is
per-worktree), WRITE_SCOPE line must start a line in the prompt; the
nested-repo refusal fires from repo root while .claude/worktrees exist —
use a scratchpad worktree via -C; stray caffeinate pid 32305 noted, kill
before any window arm; the same-signature trigger (two eaten stop-signal
misses) is RECORDED — stop-signal questions get cold review BEFORE action
now, per the verdict's process rulings.

## ▶▶ T7 CHECKPOINT (2026-08-15, Ed pause order) — superseded by T8 above; kept as record

**Nothing in flight.** The eleven-seat readiness fleet was STOPPED cleanly at
Ed's pause order (all 11 seats started, 0 completed — resume re-runs fresh,
which is preferable for audit freshness). Zero live codex processes, zero
monitors. Everything load-bearing is pushed. The 42 local worktrees (fleet
isolation + session worktrees) are ALL disposable.

**THE PLAN OF RECORD remains `docs/strategy/2026-08-14-70h-plan.md`** (read
in full; note its two Ed amendments: windows not scarce; council-gated).
**The successor's single next action: LAUNCH THE FLEET FRESH —**
`Workflow({scriptPath: "/Users/edr/.claude/projects/-Users-edr-code-JouleWise/2cc5ce62-9e44-4ab2-a470-a38d9caf2826/workflows/scripts/readiness-audit-fleet-wf_84e26deb-9c1.js"})`
(a NEW run, not a resume — resumeFromRunId is same-session-only and does
NOT survive /clear; nothing is lost because zero seats completed before the
pause. The script file is DURABLE (project dir, not scratchpad) and
SELF-CONTAINED — all eleven briefs embedded, schema-forced findings. If the
script file is ever missing, the briefs are reconstructable from charter v2
lens scopes + its anti-ritual packet) —
then harvest → C-028 refuters on blockers → the cold-paired sitting per
charter v2 (`docs/process/instrument-readiness-audit-charter.md`) → council
verdict → if READY, the single Ed session
(`docs/phase_2/ed-qualification-session.md`, chained into ALPHA arm).

**STATE IN ONE BREATH:** all three packs FROZEN at 49dcc49 (tighter
1.869502 J floor; freeze log docs/process_traces/2026-08-13-freeze-execution/);
measurement checkout /Users/edr/JouleWise-measurement-20260813 (DO NOT dirty;
reboot voids arm evidence — re-author ~15 min, tools exist and are MERGED);
readiness tooling COMPLETE on main via #149 ac3fe1d (union of #146/#147/#148
+ five integration catches — incl. the LIVE real-boot-session acid: authored
evidence through the real arm generator to GO on this machine); audit
baseline PINNED 694442c (docs/process/audit-baseline-manifest.json — any
main change voids affected lens results; the successor should verify main
still equals the baseline head + this checkpoint commit before resuming, and
re-pin if doc-only commits landed after).

**THIS STRETCH'S MERGES:** #149 (containing #146 registry post-freeze
reconciliation, #147 arm-time evidence author with 20-min volatile horizons
+ crash-detectable publication + clock hermeticity, #148 ten-item chain-fix
batch incl. keyboard-backlight census + D-8-prime rewrite + ED-session
scripts). Rulings this stretch (decision log): interaction contract
(magistrate rules all non-hardware/sudo; batch Ed sessions), M-1
BRACKET_SESSION_ID, M-2 draft-status (forward-only generators). Paper:
boundary wording narrowed at five sites (JW-MET-1). T6 run report LANDED
(docs/run_reports/2026-08-13-t6-session.md, attestation appended).

**SUCCESSOR DESK DEBT:** C-058 council entry (the record since T6's
coverage cutoff: the #146-#149 arc, the union's five catches, the fleet);
consistency sweep over the whole span (owed before the next bookkeeping
close); FLAKE-CALEXITS-311-REDERIVE fix shape registered not implemented
(4 occurrences); WO-CRASHMATRIX-RELIABILITY (bench canonical suites carry
the known 3-test load-pathology trio — disposition recorded each time).

**ED-OWED (single batched session, ping when council READY):** the
ED-QUALIFICATION script steps 1-5 (~20 min: sudo grant, sampler checklist,
rail probe, backlight control, tap walkthrough) + chained ALPHA arm if GO.
NO REBOOT of the Mac preserves the frozen evidence (else cheap re-author).

## ▶▶ T6 SESSION CHECKPOINT (2026-08-13 night) — superseded by T7 above; kept as record

**THE MILESTONE: ALL THREE PACKS ARE FROZEN at head 49dcc49** — first freeze
in the project's record, at the TIGHTER 1.869502 J floor (D-133 cl.4
executed, Ed-ratified). U11 identity-pin projections frozen ×3 (GAMMA with
its four ordered units); D-134 freeze receipts PASS ×3 (arm_disposition
NOT_APPLICABLE); the twelve evidence receipts per pack authored from primary
bytes by the #145 tool (lead-run, boot session DA90818C…); §5C LEAD LIVE
VERIFICATION discharged on the frozen checkout (dry-run-0001, four
hash-bound checks PASS). Execution record + deviations (X-2 revert-reorder,
condition-8 synthesis amendment, X-8 ruling):
docs/process_traces/2026-08-13-freeze-execution/freeze-log.md. Measurement
checkout: /Users/edr/JouleWise-measurement-20260813 (.venv+mlx; DO NOT
touch; NO REBOOT before T-0 or evidence re-authors — tool exists, ~15 min).

**SEVEN PRs MERGED this session** (T6-mechanic corrected count — #138 was T5's, merged pre-stop-order and counted in C-057): #140, #135, #141 (§5C), #142 (CH-1),
#143 (WO-COLLECTION-MARGIN-01), #144 (tighter-floor re-spec), #145
(WO-EVIDENCE-AUTHOR-01 — through a mandatory rule-11 COLD GATE, custody
docs/process_traces/2026-08-12-evauth-coldgate/). Plus: item-(1) ruling,
FLAKE-CALEXITS-311-REDERIVE root-caused (3 certified reruns), C-057 + T5
run report landed, Ed's rulings recorded.

**ARM SLIPPED TO 2026-08-14 (Ed ruling, decision log):** the packet
finalization found the launch-blocking §0.6 gap — 15 ARM_ONLY rows have no
evidence producer (arm-side mirror of X-1). **WO-ARM-EVIDENCE-AUTHOR-01
registered (TASK_QUEUE) = tomorrow's day work**, full gauntlet, deadline
before the 08-14 arm. The operative packet (111 cells filled, 34 AT-T0):
~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md.
Ed-owed at arm: M-1 BRACKET_SESSION_ID ratification, M-2 draft_status
contradiction ruling, sudo/powermetrics checklist, §5A taps.

**THE PLAN OF RECORD IS `docs/strategy/2026-08-14-70h-plan.md` — read it in full and execute from the earliest incomplete item.** In brief: (1) WO-ARM-EVIDENCE-AUTHOR-01
(build+gauntlet), (2) T6 run report + council entry + skill rows +
consistency sweep (the session record is LARGE: eight merges, two cold
gates, the freeze), (3) arm 08-14 evening.**

## ▶▶ T5 FINAL CHECKPOINT (2026-08-12, Ed stop order) — superseded by T6 LIVE above; kept as record

**Nothing in flight.** All Sol runs harvested, all monitors/watchers stopped,
zero live codex/suite processes at checkpoint. Everything load-bearing is
pushed; two bookkeeping drafts live on local disk (below).

**TEN MERGED this session:** the full T4-late queue 6/6 — #132 (fallback
respec, freeze lane unblocked), #133 (paper default-floor mainline +
mechanical tighter-floor swap block), #131 (U11 projection; **D-131
ADOPTED** 14879e4), #127 (calexits reliability), #134 (FCM-01 + integration
fix rounds), #129 (CI proof restructure) — then #137 (p2038 clock-phase
flake root fix), #136 (D-135 advisory site budgets), #139 (calexits
mutation classifier; killed the 3x hosted flake), **#138 (Q8 p256 floor
cells — packs now 100 members/pack, Ed budget ratification owed)**.
**D-136 minted mid-session (Ed): the site/Lakebed lane is RETIRED from all
automatic processes — zero tokens on it, site workflow manual-dispatch
only.**

**OPEN PRs, both one step from merge:**
1. **#140 WO-MINT-ESTIMATOR-VOCAB** — gate COMPLETE: cold-gate conditions
   F1–F12 all met (custody: docs/process_traces/2026-08-12-mintvocab-coldgate/
   — packet + 3 rulings; the paired refuter caught a live binding-seam
   fail-open both earlier condition sets would have certified), independent
   attestation + focused re-attestation, magistrate canonical suites at
   a15fe02 green outside the registered WO-CRASHMATRIX class (failing
   modules byte-identical to main). Was 10 pass / 2 pending at stop.
   **Successor: confirm CI green → D-121 comment (the F1–F12 conformance
   table is in the mintvocab director's final reports) → merge. ON MERGE,
   D-133 cl.4's conditional FIRES ON ITS OWN RULED TERMS: ALT-D120 + the
   terminal delta + mintvocab all landed pre-freeze-wave → packs re-spec to
   the tighter 1.869502 J floor (vs 8.611855 J default) via a separate
   generator run + gate; the funded p256 arm likely publishes instead of
   not-resolvable; paper swap is mechanical (#133's merged conditional
   block). Surface to Ed before executing the re-spec.**
2. **#135 crash-matrix exclusive CI job** — content refuter-fixed (120-min
   honest ceiling; WO-CRASHMATRIX-RELIABILITY registered in TASK_QUEUE);
   its CI has repeatedly failed to trigger (three pushes + close/reopen);
   head 66f6129 force-pushed to retrigger at stop. Low stakes; merge when
   its CI finally runs green + D-121.

**§5C READINESS STREAM — FULLY VERIFIED, awaiting PR only.**
`integration/5c-readiness` @ **5a80e39** (pushed): three branches merged
clean in ruled order (fix/5c-code 4ff4072 → impl/5c-readiness-records
46eb6a9 → fix/5c-docs fc4095f). Full gauntlet record: 3-lens review at
3a140bb (lens A found a LIVE derive-never-enter forgery — operator-attested
conclusion reaching a forged GO — fixed + delta-re-audited; 2/35 WEAKER
predicate transcriptions bench-repaired; D-132 applied: converging
instrument, guard armed at count 2 — a THIRD weaker-than-contract row/site
from here = consult); doctrine run 2-of-2 + E-fix rounds complete (IR-1..4
ratified wordings, boot-session reboot fence = MACHINE behavior, lead
live-verified sysctl derivation); **LC-1 applied and verified: the branch's
D-136 renumbered to D-137** (main's D-136 = site retirement; re-verify the
next free number after any later mint). Magistrate Q2 suite at 5a80e39:
**3,031 OK, rc=0, zero failures**. **Successor: rebase onto post-#140 main
(re-run LC-1 number check) → PR → CI → D-121 → merge.** Carried to freeze:
BETA/GAMMA capacity minima verified when packs freeze.

**THEN the freeze lane** (all pack content now on main once §5C lands):
tighter-floor re-spec decision (Ed) → regenerate → FREEZE → U11 freeze
projections → arm packet per D-134 (custody skeleton corrected D-4/D-5/D-11
at ~/JouleWise-window-custody/t4-session-20260810/).

**ED-OWED:** (1) the gamma-arm call is now LIVE, premise updated — see #140
note above; (2) Q8 quiet-window budget ratification (~6.28 h 1.5B / ~6.48 h
7B per pack, 20% margin — REAL new bundles, not a rider); (3) live
sudo/powermetrics checklist before relying on #127's production sampler
commit; (4) §5A taps on the quiet night.

**LOCAL DRAFTS (uncommitted, on disk):**
docs/run_reports/2026-08-12-t5-window-session.md (DRAFT — needs the
14 mechanic corrections + tail outcomes folded in before landing);
scratchpad c057-draft.md (C-057 council entry + T5 skill-usage rows,
mechanic-verified with [UNVERIFIED-BY-MECHANIC] markers on
magistrate-self-reported items). Land both + skill-log rows + consistency
sweep as the successor's first desk block.

**Sol/infra lessons this session (fold at bookkeeping):** subagent-shell
background jobs are killed at ~60 min (4 timed occurrences; >45-min runs
launch from the lead shell; .status=RUNNING is not liveness); NEEDS_SCOPE
early returns are not resumable (fresh run, re-spent time); scope diffs
anchor to the MERGE-BASE never live origin/main; read-only sandbox makes
attestations spuriously red (workspace-write + write-scope [] instead);
never gate on piped suite output (near-missed twice, caught); never assert
git state without checking it in the same turn; a branch cannot mint a
globally-unique ID from a stale base — integration-tree union check is
mandatory. Session scratchpad:
/private/tmp/claude-501/-Users-edr-code-JouleWise/7c344e29-f3e2-455c-9384-1902c950c106/scratchpad
(worktrees wtB-d135/wtC-p2038flake/wtE-mintvocab/wtF-crashmx/wt138/
wtD-5c*/wtG-*/wtH-consult/wtI-calexits — all branches pushed; safe to lose).

## ▶▶ T5 MID-SESSION STATE (2026-08-12 ~05:15Z) — SUPERSEDED by the FINAL checkpoint above; kept for detail

## ▶▶ T5 MID-SESSION STATE (2026-08-12, Fable magistrate; 12h window, LIVE)

**Merge queue executed so far: #132 MERGED (03:41Z), #133 MERGED (04:04Z),
#131 MERGED (04:38Z, D-131 RATIFIED→ADOPTED on main), #127 MERGED (~05:00Z).
Remaining: #134 (one CI check pending at head 0bc4435 — the first fix-round
push silently LOST its guard hunk in a swap-file verification sequence,
restored + byte-verified; integration delta re-audit ACCEPT zero findings),
then #129 (pre-reviewed, merges last).** New PRs this session: **#135**
(crash-matrix exclusive CI job — cuts CI wall from ~1h35m to ~30min; stacked
on #127, evidence: 5317s hosted shard vs 146s bench standalone; calexits-3.11
flake rerun queued) and **#136** (D-135 advisory site budgets; refuter
REJECT round 1 on a raw-source-proxy failure gate — fixed 0bf0a8a, delta
re-audit ACCEPT; site-chain red is IRRELEVANT per **D-136** — Ed retired the
site lane from all automatic processes 2026-08-12: no tokens on Lakebed/
capsule anything, site workflow manual-dispatch only, site results never
gate or prompt work).

**Streams in flight:** §5C readiness-record generator (D-134; xhigh Sol run
~1h+, director split it into run 1 = registry/CLI/schemas/pack slots +
Markdown views, run 2 = clause-9 doctrine prose — ratified); Q8 p256 floor
cells (round 2 after a correct impossible-proof early return; NOTE: p256
cells are REAL new bundles — 50→100 members/pack, new quiet-window budget
for Ed to ratify — not a rider like p128); WO-MINT-ESTIMATOR-VOCAB (Sol
resumed under scope grant; **COLD GATE COMPLETE** — packet + 3 rulings
custodied at docs/process_traces/2026-08-12-mintvocab-coldgate/: option A
authorized under self-contained conditions F1–F12; the paired refuter caught
a REAL binding-seam fail-open both prior condition sets would have certified
AND proved the first remedy inert — fix round under F1–F12 required before
merge); p2038 clock-phase flake root-fix (Sol implementing; kills the ~1.6%/
run CI flake that hit #127/#121).

**Freeze-lane ORDER CORRECTION (freeze-prep director, verified):** the
T4-late checkpoint's lane ("freeze → U11 projections → arm packet") is
inverted — D-134's §5C registry + receipts and the Q8 cells are pack
CONTENT, so the true order is **#134+mintvocab (if in time) → §5C run 1+2 →
Q8 cells → regenerate → FREEZE → U11 freeze projections → arm packet**.
Both control docs re-cut accordingly (readiness rows b32220e; freeze-plan
WOs 1–4 all CLOSED). Arm-packet skeleton rescued to
~/JouleWise-window-custody/t4-session-20260810/ and its D-4/D-5/D-11
corrections applied (census literal, idle-before-ledger, two-tap morning).

**ED-OWED (updated):**
- **Gamma-arm premise SHIFTED (flagged, not decided):** D-133's default
  (freeze doesn't wait; tighter floor banks for ICPE) was priced on freeze
  imminence. The freeze actually waits on §5C+Q8 regardless — days, not
  hours — while FCM (#134) is one CI check from merge and mintvocab is
  implemented pending its cold-gate fix round. If both land pre-freeze-wave,
  D-133 cl.4's re-spec-back fires ON ITS OWN RULED TERMS: packs freeze at
  1.869502 J instead of 8.611855 J and the funded p256 arm likely publishes
  instead of not-resolvable. No reinterpretation is being made — the session
  is simply executing fast enough that the ruled conditional may fire. If Ed
  wants the freeze to WAIT for it explicitly (reversal condition 5), that is
  Ed's call; PR #133's merged conditional-insert block makes the paper swap
  mechanical either way.
- Q8 quiet-window budget ratification (p256 = 50 NEW bundles/pack, hours
  recomputed by the stream — RATIFICATION-REQUIRED row in its report).
- Live sudo/powermetrics checklist before relying on #127's production
  sampler commit at arm time. §5A taps on the quiet night. Extension-axes
  roadmap review (standing).

**Session records so far:** T4-late addendum landed (b670c8f, 6 record
anomalies incl. D-131-was-branch-only and the C-056 span boundary);
control-doc batch b32220e; D-131 ADOPTED flip 14879e4; mintvocab cold-gate
custody 82b048e/529188a. Scratchpad:
/private/tmp/claude-501/-Users-edr-code-JouleWise/7c344e29-f3e2-455c-9384-1902c950c106/scratchpad
(worktrees wt131/wt134=diag134/wtA/wtB-d135/wtB-review/wtC-p2038flake/
wtD-5c/wtE-mintvocab/wtF-crashmx/wtG-q8; all branches pushed).

**SUPERSEDED by the T1 checkpoint (2026-08-08 night) below.**

## ▶▶ RESUME SCRIPT FOR THE 40-HOUR WINDOW (post-/clear; read FIRST)

**SUPERSEDED by the T1 checkpoint (2026-08-08 night) below.**

**THE PLAN OF RECORD IS `docs/strategy/2026-08-08-40h-plan.md` — read
it in full and execute from the earliest incomplete item.** In one
line: Phase A (trust/recovery/writer-literal/estimator/U11/U2 reworks —
ALL DESIGNS ADOPTED, consult memos custodied and cited in the plan;
execution + full D-118/D-121 gates) → Phase B (packs generated AND
frozen; Ed rulings D-122/D-123 in hand) → Phase C (Window ALPHA night 1,
BETA night 2, gamma if hours remain; Ed does §5A taps only). Morning
mints put the FIRST MEASURED NUMBERS in the paper.

Standing context that survives /clear: D-121 terminal magistrate
review binds every merge; the same-signature escalation trigger is
armed (three fired 2026-08-07/08 — consult, never round three); Codex
service tier: DEFAULT is the norm (Ed 2026-08-09 cut fast ~60%; override
the wrappers' old fast default with `CODEX_SERVICE_TIER=default` per call;
fast only for the single milestone-gating run); CODEX ONLY, never
Anthropic fast. Use codex-run-v3 for enforced-WRITE_SCOPE
implementations (prompt needs a literal `WRITE_SCOPE: [...]` line;
CODEX_APP_BRIDGE=off for concurrent bridge runs); review agents get
isolation:worktree and a no-checkout line; never gate on a piped test;
quiet windows need a caffeinate-free machine (kill any stray
keep-alive before arming). Ed's remaining owed rulings: the original
8 minus 2/4 (ruled as D-122/D-123); ruling 8 still gates the
reason-code SPEC lane only.

The MORNING STATE block below records how the overnight ended;
everything under it is executed history.

## ▶▶ T4-LATE FINAL CHECKPOINT (2026-08-12, Ed stop order) — /clear-SAFE; A NEW SESSION STARTS HERE

**One line: six PRs are open, every one has PASSED its independent
adversarial audit, and all are waiting only on CI wall-clock; merge them
in order with a D-121 terminal review each, then launch the two staged
implementations, then the freeze lane.** Everything below is pushed;
nothing lives only in a dead session's scratchpad.

**THE MERGE QUEUE (order matters; D-072 standing self-merge applies after
each PR's D-121 terminal review at its final head; CI must be green):**
1. **PR #132** (fallback `respec/d124-withdrawn`) — MERGES FIRST; the
   pack-freeze lane unblocks AT THIS MERGE per D-133 O1 and nothing
   FCM-shaped may gate it. Gate audit ACCEPT (substance) + staleness
   sweep applied.
2. **PR #131** (U11 identity-pin projection, D-131) — four-round gauntlet
   complete, final delta ACCEPT. Its merge unlocks the staged §5C
   implementation (D-134).
3. **PR #127** (calexits test-infra) — audit synthesized ACCEPT
   (FIND-1 routed to WO-SAMPLER-SUPERVISOR). Production commit still held
   for Ed's live sudo/powermetrics checklist.
4. **PR #133** (paper train G) — default-floor mainline; carries the
   CONDITIONAL-INSERT-TIGHTER-FLOOR swap block for Ed's pending call.
5. **PR #134** (FCM-01, D-133 desk thread COMPLETE: rounds 5-10, O2+O3
   discharged, round-10 delta ACCEPT no-findings; site-chain green after
   dedup 479eefc).
6. **PR #129** (CI restructure) — delta ACCEPT-FOR-MERGE with the
   head-bound 23-job hosted campaign green at EXACT head 35f1fe5 (run
   31541829071) = D-130's second independent execution DISCHARGED.

**STAGED IMPLEMENTATIONS (contracts custodied in
`docs/process_traces/2026-08-11-staged-contracts/`):**
- **WO-MINT-ESTIMATOR-VOCAB** (launches after #134 merges, stacks on that
  branch's code now in main): three-site spec-authoritative estimator
  dispatch — contract `mintvocab-impl-contract.md` (consult verbatim
  inside; design adopted in TASK_QUEUE). Full D-118 gauntlet.
- **§5C readiness-record generator** (launches after #131 merges): D-134
  ten-clause contract (trace
  `2026-08-11-5c-readiness-contract/consult.md`) — two-stage receipts,
  row registry, doctrine amendments enumerated in the consult.

**OWED (successor desk work):**
- **D-135 implementation** (Ed ruling, minted this checkpoint): make ALL
  conservative site budgets WARN-ONLY in scripts/pack_capsule.py + the
  site test suites; only the physical Lakebed 1,048,576-byte cap (real
  validator, CI-only — lakebed is NOT installed on the bench) may fail
  anything. Content is never trimmed for advisory budgets.
- Freeze lane after #132+#131: freeze plan (Q1/Q8 ruled, Q7 void, addendum
  items (1)+(3) LIVE per the item-level disposition on the fallback
  branch) → FREEZE → U11 freeze projections → arm packet per D-134
  (discrepancy resolutions ready:
  ~/JouleWise-window-custody/t4-session-20260810/arm-packet-discrepancy-resolutions.md).
- Q8 p256 prefill floor cells build (launches on post-#132 main).
- T4-late run-report addendum for the final block (D-134/D-135, PR queue,
  the content-filter + timeout + recovery-resume tooling classes — all
  three are in ~/.claude/skills/skill-usage-log.md).

**ED-OWED (nothing blocks tonight without them):**
- **Gamma-arm schedule call (D-133 flag)**: tighter-floor-in-main-paper
  would make WO-MINT-ESTIMATOR-VOCAB critical path and hold the freeze
  wave; default = freeze proceeds, tighter number banks for ICPE. The
  quantified stake: default floor 8.611855 J leaves the funded p256 arm
  ~3 J margin (likely publishes not-resolvable); tighter 1.869502 J
  leaves substantial margin. Paper PR #133 carries the mechanical swap
  either way.
- Live sudo/powermetrics checklist (#127 production commit).
- Extension-axes roadmap review; §5A taps on the quiet night.

**Key context for a fresh session:** D-131 (U11 contract, lands with
#131), D-132 (stopping rules target doom loops), D-133 (FCM disposition,
hybrid+ALT-D120 — EXECUTED, desk thread complete), D-134 (§5C receipts
contract), D-135 (site budgets advisory) are today's decisions. Cold-gate
artifacts custodied in `docs/process_traces/2026-08-11-fcm-coldgate/`
(standing rule: every sitting custodies packet+rulings before execution).
Council C-056 records the day. Sol launch rules that cost ~10 failed runs
today (explicit --timeout, workspace-write for suite-executing runs,
DEFENSIVE framing for adversarial-review prompts to avoid the Codex
cybersecurity content filter, never trust a recovery-resume envelope) are
in ~/.claude/skills/skill-usage-log.md — READ THEM BEFORE LAUNCHING SOL.

## ▶▶ T4 SESSION CHECKPOINT (2026-08-10/11, Ed 24h+ grind order) — SUPERSEDED by T4-LATE FINAL above; kept for detail

**THE MINT BAR IS LIFTED.** Trust PR #122 MERGED at `ae6af48`
(2026-08-11T03:40Z) under the full gate: 16Q delta 16/16 (T3), ci+site green,
lead full unpiped suite 2945 OK at the head, the decisive proof PROVEN by the
lead local run (OK, 3h35m, CI-identical hydration), and **D-130** — the
cold-gate decisive-venue ruling (packet + paired refuter; refuter's
hermeticity finding: the local run's legacy-locator assertion executed
against 190 LIVE machine-local decoy paths). CI proof job is ADVISORY
(dispatch-only) pending **WO-CI-RESTRUCTURE** (TASK_QUEUE; deadline: before
any claim publication and before the pack-freeze merge wave; first hosted
green = required second execution). Citation discipline until closure:
"lead-verified locally (custodied bundle: docs/evidence/d117-v2-decisive-20260811/)
+ CI-verified transport/authentication chain". Post-merge batch on main
`654c53d`; kernel UNGATED + fidelity pins cleared `b04c5bf`; Ed's temporary
settings.local.json rules removed; 3.11 decisive replay (D-130/C3) was IN
FLIGHT at this checkpoint (log scratchpad decisive-local-py311.log; harvest
result, then note it in the evidence dir).

**FLOOR-COMMONMODE-01 IS FROZEN — ED DECISION PACKET.** Frozen at `123e8a5`
(FREEZE-FCM01.md on impl/floor-commonmode-01) after the terminal cold-gate
condition executed: FIVE distinct understatement mechanisms across four fix
rounds, three cold-gate sittings, two paired-refuter reports, four delta
audits (ledger in the freeze banner; final: FCM-R4-01, zero-point value not
authenticated as the true zero evaluation, 5.0e-10 J admitted-input exact).
The PRODUCTION path is unaffected (it computes z itself); the failures live
on the direct-call any-admitted-input contract. **Ed's options** (freeze-plan
Q7 bars pack freeze while the estimator is candidate-pending): (i) relicense
with a structural zero-threading contract (candidates in the freeze banner);
(ii) reverse Q7 + re-spec both floor packs' comparative cells to the
worst-case default (COSTS the funded p256 prefill contrast's claim
capability — the gamma arm likely publishes as unresolvable); (iii) hold.
The frozen gauntlet record is itself paper material (the refuter's argument).
Also banked for Ed: the two cold gates' process recommendations (registered
text may claim only what its committed oracle exercises; delta audits report
in ulp-of-largest-intermediate units; class-keyed same-signature counting).

**PAPER — full Rivoire-bar program executed on branch paper/edit-train-t4**
(trains A-D + three schematic figures, all magistrate-reviewed): D-122
currency fixed at 7 sites; the two REQUIRED missing limitations added
(D-124 stationarity/applicability, sampling resolution); all three metrology
blockers corrected (95/95 conditionality, ABBA honest scoping, the false
floor-guarantee); L23's seven currency/provenance residuals; the terms/
physics program (glossary, physical explanations, coherence fix); train C
related-work overhaul (JouleSort triad restored to Rivoire's actual list,
verified lineage subsection w/ 4 new refs incl. two of the advisor's own,
five S1 advisor-visible defects fixed, full renumbering to 23 refs
mechanically verified); train D structure (13→11 sections, plain abstract,
figures integrated w/ the interval-conservation sensitivity caption).
Train E landed; magistrate full linear read done (caught duplicate table
numbers + figure ordering); **PAPER MERGED as PR #126** (`0cf5f84`,
2026-08-11T10:19Z — GitHub scheduled no CI for the docs-only PR; the
docs-adjacent suites were run locally as equivalent evidence, recorded in
the D-121 comment; the trust-vs-train-E custody conflict resolved with the
branch's superset text). Draft now waits on measured numbers via the fill
registry; pre-submission owes: L5's UNVERIFIED re-checks (HotCarbon/IISWC
programs), report_src drift decision.

**T4 late additions:** D-130 condition C3 discharged (3.11 decisive replay
green, 4h18m — evidence committed); the site-lane anchor break (D-130
heading `#`) found by the T4 bookkeeping director, fixed `4888cb8`; T4 run
report + council C-055 landed (`42b7a7b`); the `test_calibration_exits`
reliability class hit count 2 (main CI teardown-race recurrence) → the
standing-trigger CONSULT ran (root causes: detached git auto-maintenance
writer; CPU-amplifying fake fixtures; silent 68-case monolith; plus a REAL
production sampler-reaping gap in validate_powermetrics_fiducial.py) → the
adopted composite design ran its FULL gauntlet in-session (refuter 3
blockers → fix → delta 2 blockers → a SECOND count-2 consult on the
sampler-ownership class, whose ruling REMOVED the identity machinery in
favor of the narrow honest fix + detect-only census, with the supervisor
design registered as WO-SAMPLER-SUPERVISOR incl. its sudoers-migration
prerequisite) — **PR #127 OPEN**; its CI begins the ten-hosted-greens
closure count. LEAD-OWED before relying on the production commit: the live
sudo/powermetrics checklist (module docstring). Successor: #127 CI → D-121
→ merge.

**MERGED THIS SESSION: #122 (trust/mint bar), #124 (WO-2), #125 (WO-3 —
replay-derived receipt oracles all three packs), T3 bookkeeping `e74cc4c`,
runbook drift-allowance correction `4d3e3ad`, freeze-plan addendum `51bcf77`
(lineage-monotone margin risk), D-130 batch `654c53d`, kernel clear-back
`b04c5bf`.** Arm-packet skeleton drafted (custody:
~/JouleWise-window-custody/t4-session-20260810/ + scratchpad
arm-packet-alpha-SKELETON.md) with 12 RECORDED arming-surface discrepancies
(dual final-readiness commands; caffeinate contradiction; settle ownership;
U11 tool DOES NOT EXIST — freeze-lane critical path) — resolution pass rides
the freeze lane.

**Owed (successor desk block):** T4 run report + council entry (the FCM
adjudication chain + D-130 + the paper program; dictated-fills via Opus
director worked for T3 — reuse); skill-usage rows for T4; harvest the 3.11
replay + train E; prune trustverify/papered/fcm worktrees when their lanes
close (fcm worktree holds the FROZEN branch — keep until Ed rules);
cs-pedagogy worktree audit item still stands (Ed decision wanted).
Process notes: two-writers-one-worktree caused a scope-violation misfire
(figures committed mid-run) — never again; inline codex-run-v3 prompts
without the literal WRITE_SCOPE line = rc 64 (5th recurrence, prompt-file
rule now logged); delta-audit prompts must REQUIRE exact-arithmetic verdicts
printed (delta-2 computed and dropped one — highest-value process finding of
the FCM episode).

## ▶▶ T3 SESSION FINAL CHECKPOINT (2026-08-09 evening, Ed wrap order) — SUPERSEDED by T4 above; kept for detail

**Session shape:** first full session under D-129 (fan-out standing order,
~60% fast-tier cut, Fable-economy-with-full-coverage — all three minted this
session from Ed's in-thread directives). Peak ~9 concurrent streams. Durable
custody of all session artifacts (reports, statuses, flake-loop log, the
8038ccd full-suite log): `~/JouleWise-window-custody/t3-session-20260809/`.

**LANDED/MERGED this session:** flake fix **PR #123 MERGED** (lead 8x loop
8/8 + Sol 30-loop + D-121); T2 bookkeeping (run report + C-053, `7fde68b`) +
council-index repair (`966dd39`); WO-4/Q9 prefill phase proof **DISCHARGED**
(`2cd9bc3` — 7B PROVEN, 1.5B PROVEN-WITH-CAVEATS incl. the p256-cell
resolution-pressure warning); extension-axes H1/H2 roadmap DRAFT (`e9c2433`,
Ed review tap); site-renderer silent-64KiB-truncation bug FIXED (`955df9b`);
consistency sweep applied + D-129 minted + state kernel → T3 gate
(`50d1064`); 12 stale worktrees pruned; release
`fixture-d117-v2-production-v1` PUBLISHED (sha re-verified by fresh
download).

**TRUST (PR #122) — one CI gate from the mint-bar merge.** Branch
`impl/d117-postcollection-trust-clean` head `e871f5b`: clean resynthesis
(zero custody blobs reachable, single-parent verified) + fsum
cross-interpreter fix (`e376e8c`) + guard parcel (`99d0e9b`) + guard
hardening (`f588f86`, io/codecs misparse + fail-closed pins) + custody-store
plumbing rounds 1+2 (`e807d5f`, `e871f5b`). **16-question delta: 16/16 PASS**
(initial 14 + Q10/Q3 fix-then-regrade, Opus graders + refuters). Decisive CI
history: round-1 fail = latent plumbing gap (campaign never received the
store; T2's green runs silently read Ed's machine-local/iCloud paths — NOT
merge-introduced, present at a89f279); round-2 fail = the NEW hermeticity
assertion correctly caught a second unplumbed read site (candidate
rediscovery); both fixed, hermeticity kept strict (no narrowing).
**SUCCESSOR: (1)** confirm `d117-production-proof` green on `e871f5b` (was
in flight at wrap; on fail: full log + NEW-signature check — two rounds are
spent, a third same-class failure ⇒ standing escalation = consult, never
round 3); **(2)** lead full unpiped suite at the final head (8038ccd suite
was green 2934/86-skip; the four parcels since are focused-verified only);
**(3)** D-121 terminal review at final head; **(4)** merge = **MINT BAR
LIFTS**; **(5)** then bench: kernel gate clear-back (test_gen_state pins →
[], per their notes), remove Ed's temporary history-rewrite + `gh release`
rules from `.claude/settings.local.json`, finalize the PR ledger
(deferred-with-record: 16Q Q1 residuals — silent no-session fallback,
missing session assertion in the mint body; `_locked_append` line-anchor
uniformity).

**FREEZE LANE:** WO-2/Q5 byte-identity **PR #124 OPEN** (lead-replayed both
interpreters; CI + D-121 then merge). WO-3 receipt-oracle re-derivation:
NOT STARTED (was queued behind WO-2; launch off post-#124 main).
**FLOOR-COMMONMODE-01 BANKED UNGATED `425f75f`** (impl/floor-commonmode-01,
pushed; all six D-124 registration conditions structurally enforced per the
Sol report; based on trust head 8038ccd) — **successor's first big block:
full magistrate audit + D-118 gauntlet, rebase onto post-trust main, land,
then p256 floor cells (Ed-funded Q8) → regenerate packs → freeze.**

**Process notes for the record:** three Sol rounds were burned by the
F3-class read-only-sandbox launcher trap (always `-s workspace-write` +
writable TMPDIR); the stale `.claude/worktrees/cs-pedagogy-ai-cf3aed`
worktree BREAKS codex-run-v3 strict-scope launches (nested-repo refusal) —
audit item stands, decision wanted; never pkill by pattern on a shared
machine (killed a sibling's suite run); WO-4's resolution caveat feeds Q8
planning (p256 1.5B prefill windows will carry the same
not_resolvable_sample_count pressure).

**Owed bookkeeping (successor desk block):** T3 run report + council C-054 +
skill-usage rows; prune this session's worktrees after the trust merge
(trustasm/flakeverify/fix1/guardfix/fcm/wo2/wo4/axes/bookkeep + diag1/diag2 —
all branches/artifacts pushed or custodied).

## ▶▶ T2 SESSION FINAL CHECKPOINT (2026-08-09 ~08:30) — SUPERSEDED by T3 above; kept for detail

**Nothing in flight** (all Sol runs harvested; flake-verify loop stopped mid-run
harmlessly). Durable custody of every load-bearing session artifact (trace
notes, all Sol reports, THE THREE RESOLVED TRUST FILES):
`~/JouleWise-window-custody/t2-session-20260809/`. Session scratchpad (tmp, may
vanish): `/private/tmp/claude-501/-Users-edr-code-JouleWise/6811852b-72f8-4299-b497-3c4949e29b9d/scratchpad`.

**SESSION RESULT: 5 PRs MERGED** (#117 packs, #118 recovery→ARMING code+
procedure discharged, #119 operator surface, #120 results scaffold, #121
methods+draft), suite-green repair + prose-linter 3.11 fix + T1 bookkeeping on
main, pack-freeze plan RULED (incl. Ed's Q1/Q8 taps + "better paper" guiding
light — see memory + docs/strategy/2026-08-09-pack-freeze-plan.md), trust mint
bar PROVEN + landing fully integrated pending final assembly.

**SUCCESSOR ORDER:**
1. **TRUST LANDING — final assembly (all judgment DONE, ~1h mechanical+gates):**
   R1 IS ADJUDICATED AND SECURITY-APPROVED (magistrate): 3 evidence reads
   routed through read_authentication_input (legacy-journal metadata, physical
   ledger JSONL, frozen reservation plan); 6 descriptor/OS-metadata sites
   narrowly exempted via line-anchored CLASSIFIED_NON_AUTHENTICATION_READS
   entries w/ per-site justifications; guard 14/14 green + 106 focused green
   (Sol in-run). The THREE RESOLVED FILES (calibration_ledger.py,
   decision_log.md, test_authentication_io.py) are custodied at
   `~/JouleWise-window-custody/t2-session-20260809/`. ASSEMBLY (method doc =
   docs/strategy/2026-08-09-trust-landing-integration.md): fresh worktree off
   CURRENT origin/main → `git merge --no-commit safety/trust-a89f279-checkpoint`
   → overwrite the 2 conflicted files (+ guard test) with the custodied
   resolved versions → `git rm -r --cached` custody_store content subdirs
   (keep manifest.json) → verify `git ls-files | grep 'custody_store/[^/]+/'`
   EMPTY → **`git commit-tree <tree> -p origin/main`** (sever dirty ancestry)
   → verify `git rev-list --objects | grep custody_store/.*/ ` EMPTY → full
   suite (green now that the flake fix exists — merge/land it first or run
   with it) → PUBLISH release fixture-d117-v2-production-v1 (CI job downloads
   the asset anonymously; archive at 92058940 scratchpad MAY BE GONE — asset
   already uploaded+sha-verified on the draft release, publishing needs no
   local archive) → PR → CI d117-production-proof (authoritative decisive) →
   D-121 → merge = **MINT BAR LIFTS**.
2. **Flake fix branch impl/recovery-flake-fix (PUSHED, ~PR-ready):** teardown
   race fixed, Sol 30-loop + full suite green; lead 8x verify loop was cut
   short at checkpoint — rerun it, then PR→merge (it unhangs every future
   full-suite run; consider landing BEFORE the trust final suite).
3. **Then the freeze critical path (order per pack-freeze plan):**
   FLOOR-COMMONMODE-01 (D-124 estimator impl, AFTER trust merges — shared
   floor_extraction surface; full gauntlet) → p256 floor cells (Ed FUNDED, Q8)
   + the 4 engineering proofs in the freeze plan → regenerate packs → freeze.
4. **Owed bookkeeping (first desk block of successor):** T2 run report +
   council C-053 + skill-usage finalization (trace-notes.md + skill-log rows
   already appended live); consistency sweep (many docs touched); worktree
   pruning (tmp worktrees: trustclean/flakefix/packfam/recint/oplane/rlane/
   m1lane/u5-7pack/tv-* — ALL branches pushed, safe to lose; also the T1-era
   stale .claude/worktrees/wf_d910c76a + cs-pedagogy audit item stands).
5. **Kernel gate T1-2026-08-08-NIGHT:** recovery clearance CLOSED; gate clears
   fully when trust merges (then update the 2 test_gen_state fidelity tests
   per their documented clear-back note).
6. **Ed's §5A/night steps remain the only path to measured numbers** once
   trust + freeze land; arm via runbook §5C (plan-bound GO record + lead live
   verification).

## ▶▶ T2 SESSION UPDATE (2026-08-09 ~07:40, Fable magistrate) — superseded by FINAL above; kept for detail

**Since the ~03:40 block below:** 3 paper PRs opened (#119 operator
arm-readiness, #120 results scaffold, #121 methods+draft — #119/#120 CI GREEN;
#121 failed on a FLAKE `test_calibration_exits` OSError Directory-not-empty
.git/objects [temp-repo teardown race, NOT the edit], reran + flake-fix in
flight impl/recovery-flake-fix). **Pack-freeze plan CUSTODIED**
`docs/strategy/2026-08-09-pack-freeze-plan.md`: magistrate RULED Q2A/Q2B/Q2C/
Q3/Q4/Q7 + 4 engineering work orders (FLOOR-COMMONMODE-01 long pole,
D-123 byte-identity, receipt-oracle re-derivation, phase-recording proof); TWO
ED TAPS surfaced — **Q1** (p256 prompt text; Sol built one w/ dual-tokenizer-
identical 256 IDs, sha 83099a66; recommend freeze) and **Q8** (fund dedicated
p256 floor cells vs narrow prefill claim).

**TRUST — mint bar PROVEN, landing method VERIFIED, one step from PR:**
- Decisive regression's failures were ALL test-precision, mint bar INTACT (every
  tampered domain refused). Sol triage: 11 stale fragments (corrected to
  canonical guard reasons) + 1 REAL coverage shadow (`primary` — summary_metrics
  tamper shadowed the bundle_sha256 guard); reworked so the guard is exercised,
  ISOLATED-PROVEN (pre=not-reached / post=reached+refuses). Corrections
  checkpoint-committed `a89f279` (tag `safety/trust-a89f279-checkpoint`).
- LOCAL final-head decisive rerun WEDGED (poll-blocked mint subprocess under
  load, killed) — belt-and-suspenders only; the attack matrix already ran
  end-to-end in the earlier 3.5h run (all 15 refused), corrected legs are
  isolated-proven + focused suites green, and CI's d117-production-proof job is
  the authoritative decisive run on the clean branch. FOLLOW-UP: investigate the
  trust test's mint-subprocess pipe handling under load (possible G4-class).
- **LANDING METHOD (Sol-designed bdltx9fh0, VERIFIED — full detail in session
  trace-notes.md "TRUST LANDING METHOD"):** clean-branch resynthesis from
  origin/main (content dirs enter git only at 1cae2bc; A-rank). 3-way MERGE of
  the 4 both-sides-changed files (calibration_ledger/whole_window/decision_log/
  test_calibration_bracketing — trust auth-core + recovery durability BOTH must
  survive), then `git commit-tree -p origin/main` to SEVER dirty ancestry (no
  blob history in main), `git rm --cached` the custody content subdirs (keep
  manifest), verify `rev-list --objects | grep custody_store/.*/` EMPTY, full
  suite, PUBLISH the release (CI downloads asset anonymously — no draft), PR →
  CI → D-121 → merge = MINT BAR LIFTS. Safety: reversible until PR merge; old
  branch preserved by tag + 55MB 1cae2bc bundle at
  ~/JouleWise-window-custody/trust-prerewrite-20260808/.
- The recorded T1 rewrite procedure (git rm --cached + amend) was found
  INSUFFICIENT (only strips tip; blobs stay in 1cae2bc parent) — do NOT use it.
- **~08:00 — trust landing ATTEMPTED, revealed a real integration seam; full
  plan custodied `docs/strategy/2026-08-09-trust-landing-integration.md`.** The
  3-way merge reduced to 4 ledger conflicts + decision-log: H1/H4/decision-log
  = clean UNION; **H2/H3 = KEEP-HEAD** (trust's `_read_append_journal` /
  `_record_append_recovery` are the OLD SIDECAR subsystem recovery
  architecturally DELETED — pasting them back = undefined-symbol dead code).
  **R1 (the real remaining work, blocker):** recovery added 9 direct-I/O sites
  in calibration_ledger.py that trust's registration-at-read guard
  (test_authentication_io) rejects — each needs a per-site SECURITY
  classification (content-read → auth helper; descriptor-only → justified
  exemption; NEVER broad-exempt = silent hole in the trust guarantee). This is
  a **careful FRESH cycle**, not a marker finish (deliberately not rushed at
  hour 9 with the suite gate still down). Throwaway merge aborted; worktree
  clean; a89f279 tag-safe. Needs the flake fix (impl/recovery-flake-fix) landed
  first so the suite doesn't hang in test_calibration_exits.
- **ALL 5 PRs MERGED tonight: #117 packs, #118 recovery-arming, #119 operator,
  #120 results-scaffold, #121 methods+draft.** #121's earlier CI fail was the
  same test_calibration_exits flake (reran green).

**MERGED TONIGHT (both under full gates + D-121 terminal review):**
- **PR #118 (`05ce39b`) — RECOVERY MERGED; the ARMING blocker's code+procedure
  side is DISCHARGED.** Cold-gate-ruled G2/G4/G6+G5 fix rounds (executed
  probes, two scoped deltas same-signature NO, mutant-kill closures), ledger
  CONTRACT durability amendment (fail-closed), runbook **§5C manual arming
  procedure** + §6 chain-owned settle. Live arming still needs: trust merge,
  pack freeze, §5C plan-bound GO record + lead live verify + Ed's §5A steps.
  Witness-integrity = separate off-path mutation-kill track (not started).
- **PR #117 (`06303b5`) — the three D-117 campaign packs ON MAIN as UNFROZEN
  drafts** (U5/U6/U7; 30-agent review + 2 fix rounds + deltas; both arms per
  D-122 in gamma). Freeze-time items reserved for Ed: 256-tok prompt
  ratification, D-122-unpinned params, receipt-oracle re-derivation (recovery
  now merged), cadence final ratification, D-125 envelope alternative.
- Also on main: T1 bookkeeping (01420da), suite-green repair (55a05e3),
  prose-linter 3.11 compat fix.

**TRUST (mint bar) — decisive regression rerun IN FLIGHT** (task bie5jp9ss,
started 01:31, hours-scale: attack matrix runs multiple audited 3.3GB mint
legs). First run failed at 105min in the TEST'S OWN attack leg (None guarded
floor — legitimate per detection_floor); bench-fixed fabricate-if-None
(stronger tamper), rides the worktree diff. On green: commit-split
(auth-core/substrate) → hydrator census → publish release → Ed-permissioned
history rewrite → 16Q delta → PR merges = MINT BAR LIFTS. Then final-head
full suite (V5 clone run died inconclusive under load; authoritative run =
final head, serial).

**BANKED branches (pushed, pre-PR):** impl/d117-operator-arm-readiness
(GO/NO-GO matrix + freeze manifest + ABORT appendix, review-fixed);
impl/paper-results-scaffold (fill registry 146 rows + figures plan +
fail-closed renderer w/ vocabulary-sync tripwire, 26 tests);
impl/paper-methods-audit (M1 memo: 2 BLOCKER + 4 SHOULD-FIX for the draft
edit train). PR wave after trust.

**IN FLIGHT:** trust decisive (bie5jp9ss); post-merge cross-stream
integration review (bjk1oxdn5). Session scratchpad:
`/private/tmp/claude-501/-Users-edr-code-JouleWise/6811852b-72f8-4299-b497-3c4949e29b9d/scratchpad`
(trace-notes.md = full trace; worktrees: packfam/recint/oplane/rlane/m1lane/
u5pack/u6pack/u7pack + tv-parity/tv-suite clones — u5/u6/u7pack + tv-* +
recint prunable after trust lands).

**Ed directives tonight (durable):** Sol counter-reviews LEAD-authored
specs/designs frequently, Fable adjudicates best-of-both (validated 3-for-3
tonight: fix contract, §5C procedure — both materially improved); consults
parallel never blocking; decompose 2h+ serial verification into parallel
atoms; Fable retains orchestration + all final reviews.

**Kernel gate T1-2026-08-08-NIGHT:** recovery clearance CLOSED by #118; gate
stays until trust proof verification closes (then clear gate + update the two
test_gen_state fidelity tests per their documented clear-back note).

## ▶▶ T1 SESSION FINAL CHECKPOINT (2026-08-08 night, Ed stop order) — /clear-SAFE; READ FIRST

**Nothing in flight — all codex processes killed, workflow stopped.**
Scratchpad:
`/private/tmp/claude-501/-Users-edr-code-JouleWise/92058940-b39f-4e0e-aed5-3be9f831f90f/scratchpad`
(trace-notes.md is the full running trace of this session). Worktrees
under `…/377d50a5-…/scratchpad/{trust,recovery,u2rework}`.

**SUCCESSOR ORDER (Phase A continuation; D-128 governs):**
1. **RECOVERY (arming blocker) — the cold gate RULED; the ruled fix
   round did NOT land.** Branch impl/d117-ledger-recovery @ `e265c9c`
   (cold-gate ruling custodied). The G2/G4/G6 arming-path fix round was
   killed before writing anything (recovery worktree is CLEAN — work
   not-started, relaunch fresh). Contract:
   `<SP>/recovery-armfix-prompt.md`. It implements ONLY the three
   first-occurrence production defects the cold gate licensed (FIX-A
   G2 genesis dirfd-binding; FIX-B G6 crash-auth unlink-only-on-valid;
   FIX-C G4 runner timeout) with EXECUTED probes, per
   COLD-GATE-SYNTHESIS.md on the branch. Then scoped delta → lead
   replay → integration tree vs main → PR → CI → D-121 → merge
   discharges ARMING. The witness-integrity MUTATION-KILL HARNESS is a
   SEPARATE off-critical-path track (do NOT try to re-harden the FIX-14
   AST gates — PROHIBITED by the cold gate). L1 witness-integrity
   limitation is surfaced for Ed's review (COLD-GATE-SYNTHESIS §4).
2. **TRUST (mint bar) — round 2c (verification tail) ran; HARVEST from
   disk.** Branch impl/d117-postcollection-trust head `1cae2bc` +
   uncommitted 2c work; worktree diff is ground truth (report may be
   thin — recover via `codex-bridge resume` if needed). Round 2b PROVED:
   reduce.py pinned, auth-core suites green, ONE authentic unpatched
   production mint. Round 2c was completing the ~68-min decisive
   regression (auditor already repaired 193/193) + v1 parity + full
   suite. On harvest: LEAD-VERIFY the load-bearing proofs yourself →
   commit-split (auth-core vs substrate parcels) → publish the DRAFT
   RELEASE (already created+uploaded+sha-verified:
   fixture-d117-v2-production-v1, archive sha f1286bc8…; publish AFTER
   a hydrator census) → HISTORY REWRITE (Ed's 4 permission rules cover
   it; exact commands in trust-fixture-substrate/RULING.md addendum;
   the 38 content dirs leave git per the substrate ruling) → 16-question
   Workflow delta → PR. Safety bundle for the pre-rewrite state:
   tag `safety/trust-1cae2bc-prerewrite` + 53MB verified bundle in
   `~/JouleWise-window-custody/trust-prerewrite-20260808/`.
3. **U2:** still FROZEN count 3 (branch 5b00200) — post-window cold gate.

**LANDED to main this session (all pushed):** T0 bookkeeping
(`d81c78a`); substrate RULING + addendum (`8788891`/`b7aad49`); **Codex
Fast Mode = STANDING DEFAULT** both routes (`de759c9`; Codex-only,
never Anthropic — Ed); recovery ESC-2 consult+adoption (`bc01908`) +
delta-1 FAIL + FREEZE (`0c30993`) + COLD-GATE ruling (`e265c9c`, on the
branch); consistency-sweep fixes (`2ba514a`). Skills folded (live on
disk, ~/.claude not versioned): parcel-by-footprint default,
neutral-SE refuter phrasing, --write-scope-lock trap, parallelism-is-
default. Memory: instrument-mix superseded (fast default);
rust-rewrite-witness-integrity (Ed floated Rust — HARD NO for MVP, P3).

**ED DIRECTIVES THIS SESSION (durable):** fast everywhere for Codex,
Claude scarce/lean; HARDER PARALLELISM (Workflow fan-outs for read-only,
footprint-parceled implementation, monoliths need a named reason —
validated: two 8h monoliths, one walled reportless); 4 history-rewrite
rules + `gh release:*` added to settings.local.json (REMOVABLE after
the trust PR merges); ~30h grind; paper ETA 4–6 days gated on 2–3 QUIET
nights (Ed does §5A taps), now +0.5–1.5d from the recovery cold gate.

**OWED bookkeeping (first desk block):** council C-052 (this session:
substrate ruling, fast-mode, recovery cold gate, trust wall+2c);
skill-usage log; T1 run report. **DISCHARGED by the T2 session
(2026-08-08 night): C-052 + docs/run_reports/2026-08-08-t1-window-session.md
+ skill-usage rows installed (Sol-drafted, lead-reviewed).** Trust 2c harvest + recovery armfix
relaunch are the two night-critical resumes.

## ▶▶ T1 mid-session detail (superseded by the FINAL block above; kept for pointers)

**Session = T0's successor under D-128.** Scratchpad:
`/private/tmp/claude-501/-Users-edr-code-JouleWise/92058940-b39f-4e0e-aed5-3be9f831f90f/scratchpad`
(trace-notes.md is the running trace). Worktrees still under
`…/377d50a5-…/scratchpad/{trust,recovery,u2rework}`.

**LANDED on main this session (all pushed):** T0 owed bookkeeping —
run report `docs/run_reports/2026-08-08-t0-window-session.md` + council
C-051 + skill-usage (`d81c78a`); fixture-substrate RULING
(`8788891`+addendum `b7aad49`); **Codex Fast Mode is now the STANDING
DEFAULT** on both `scripts/codex-bridge` (`de759c9`) and (Ed-authorized
in-place) `~/.local/bin/codex-run-v3` (backup
`codex-run-v3.bak-20260808-prefast`); `CODEX_SERVICE_TIER=default`
opts out. Fast = CODEX ONLY, never Anthropic fast (Ed).

**ED DIRECTIVES THIS SESSION (durable):** (a) fast everywhere for
Codex; Claude/Fable scarce, stays lean. (b) HARDER PARALLELISM —
read-only layers are Workflow/parallel fan-outs; implementation
parcels by disjoint footprint; long single streams need an explicit
reason (validated: two 8h monoliths this session, one hit the wall).
(c) 4 history-rewrite permission rules added to
`.claude/settings.local.json` + `gh release:*` — REMOVABLE after the
trust PR merges. (d) ~30h grind window; paper ETA 4-6 days gated on
2-3 QUIET nights (Ed does §5A taps), now +0.5-1.5d from the recovery
cold gate below.

**RECOVERY (arming blocker) — FROZEN at unexecuted-proof COUNT 3 →
COLD GATE, not a fix round** (`0c30993`, pushed; branch
impl/d117-ledger-recovery). FIX-14..18 landed (`4495609`) but the
parallel 6-lens delta 2 returned ALL SIX NOT-CLOSED; G1 reproduced the
unexecuted-proof class at count 3 (EvidenceAlias fabrication + direct
readiness passed the FIX-14 gates). Same-signature 2nd occurrence on
lease (G2) + preservation (G3) AFTER the terminating ESC-2 consult →
rule-11 mandatory cold gate. **Freeze is ON the paper critical path**
(discharging recovery = the arming blocker). NEXT: convene a COLD
FABLE instance + Opus refuter on the mechanical packet
(docs/process_traces/2026-08-08-recovery-exits-escalation/FREEZE-COUNT3.md
— best done from a FRESH context, that is the point). Decomposition
question the cold gate must rule: can the CLEAN custody core + runbook
D-117 amendment land to discharge arming while witness-corpus
integrity is resolved separately? Do NOT decide alone; do NOT spawn
FIX-19. Custody core was ruled CLEAN by the escalation.

**TRUST (mint bar) — round 2b ran the FULL 8h, hit the wall, NO
REPORT** (`ACCEPTANCE_FAILED` = report_capture missing, NOT a scope
violation; all 12 changed paths in-scope). Ground truth = worktree
diff at head `1cae2bc` (uncommitted 2b work on top; branch
impl/d117-postcollection-trust). Verified at bench: reduce.py AT the
pinned SHA (5118849d); substrate deliverables all present (packager,
hydrator, `.github/workflows/d117-production-proof.yml`, transport
descriptor+test, .gitignore rule); decisive regression +539/-97.
Archive built + self-verified mid-run (SP/fixture-archive/, sha
f1286bc8…). Draft RELEASE created + asset uploaded + fresh-download
sha VERIFIED (fixture-d117-v2-production-v1, unpublished). PROOF
STATUS UNKNOWN pending report recovery (bridge resume in flight,
session 019fe33b…). NEXT: harvest recovery report → LEAD-VERIFY the
load-bearing proofs (authentic mint, ABA, bidirectional equality,
190-census, full suite) → commit-split (auth-core vs substrate — they
PARCEL cleanly) → publish release after census-via-hydrator → history
rewrite (Ed's rules cover it; the 38 content dirs leave git) →
16-question Workflow delta → PR. Substrate is a clean separate parcel
from auth-core (the lesson: should have been split at launch).

**U2:** still FROZEN count 3 (5b00200) — untouched, post-window cold
gate.

**In flight at this checkpoint:** trust report-recovery resume
(`bwp1082g1`). Recovery graders all harvested. If a /clear happens:
the cold gate + trust proof-verification are the two live threads;
both are documented above and in the branch trace dirs.

## ▶▶ T0 SESSION FINAL CHECKPOINT (2026-08-08 ~13:40, Ed stop order) — /clear-SAFE; SUCCESSOR STARTS HERE

**SUPERSEDED by the T1 checkpoint (2026-08-08 night).**

**Nothing in flight. Zero live codex processes. All branches pushed.**
Session scratchpad (prompts/reports/consult copies + checkpoint-notes.md):
`/private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad`.
Worktrees {trust,recovery,u2rework} under `…/377d50a5-…/scratchpad/` —
clean, branches pushed, safe to lose.

**SUCCESSOR ORDER (Phase A continuation; D-128 mandate governs):**
1. **TRUST (mint bar):** round 2 was KILLED mid-run at ~4h22 by Ed's
   stop order; partial state banked `1cae2bc` (pushed). Core round-2
   work landed in-tree (authentication_io, custody_store fixture 38
   content-IDs, conversions); report thin/absent — TRUST NOTHING
   without the round-2 proofs (reduce.py SHA 5118849d… revert proof,
   ABA regression, absent-mode parity, fixture hash census, authentic
   unpatched mint, bidirectional auditor equality). Resume per
   trust2-prompt.final.md + RULING-CONSULT.md from the checkpoint diff
   (fresh session; --resume ambiguous after consults ran in that cwd).
   ⚠ NEW RULING NEEDED FIRST: the fixture is 3.1GB (38×83MB plists);
   GitHub warned on push. Adjudicate substrate (LFS / thinned traces /
   generated-at-test-time) BEFORE more fixture work or any PR.
2. **RECOVERY (arming blocker):** FIX-1..13 ALL CLOSED, banked
   `468e0a6` (pushed), full suite 2770 OK in-run. Next: fresh gauntlet
   delta with THREE explicit questions — unexecuted-proof class
   (count 1), inspect-as-permission class (count 1), and the
   orphan-reaping finding (checkpoint-notes.md: harness leaked 8
   spinning SIGKILL children, lead-killed; verify reaping + whether it
   distorted suite timing). Then lead replay → integration-tree with
   post-trust main → PR → CI → D-121 → merge discharges ARMING BLOCKER.
3. **U2: FROZEN at count 3** (branch 5b00200; U2-FROZEN-COUNT3.md is
   the cold-gate packet). Post-window item. Do not touch outside a
   cold gate.
4. **D-127/D-128:** consult custodied `daf9644` (assessed sound,
   adoption = build session's first move; recovery lands FIRST).
   D-128 standing mandate: run the loop until a defensible paper.
5. **Owed bookkeeping (first desk block):** council log C-051 +
   skill-usage log + session run report (this block is the interim
   record); consistency sweep after the next merge wave.

**HARDWARE-FOOTPRINT items (Ed directive, task #8 + memory):**
405GB stale codex-run-v3 scope snapshots purged (88%→43% disk);
wrapper retention patch written but REVERTED after its test suite
failed assertion 61 (patched copy: ~/.local/bin/codex-run-v3.patched-
20260808-DEFERRED; known-good restored + verified; determine whether
assertion 61 fails PRE-patch before re-landing). Ed authorized codex
tooling changes for machine-health. Audit scope in task #8: snapshot
content (exclude runs_* corpora?), enforced-scope launch discipline,
orphan reaping, full-suite frequency, disk checks in fleet-health
cadence.

**MERGED to main this session:** results-prose template + linter
(`1e6fa16`, class ruled dead after 4 deltas — ready for alpha
numbers). **Decisions minted:** D-126 (U2 synthesis), D-127 (autonomous
loop, ratified), D-128 (standing run-the-loop mandate). **Rulings
custodied on main:** trust F1/F2 (`fe85b09`), recovery witness-scope
(`6981d2b`), D-127 consult (`daf9644`).

## ▶ T0 SESSION 2026-08-08 (40h window) — mid-session state (SUPERSEDED by the final checkpoint above; kept as history)

- Session scratchpad (prompts, scopes, consult copies, out-files):
  `/private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad` (SP).
  Worktrees: `…/377d50a5-…/scratchpad/{trust,recovery,u2rework}`.
- **DONE: RESULTS_PROSE landed on main (`1e6fa16`)** — fillable results
  template with terminating conditional structure + fail-closed linter
  (15 refusing mutations); the unconditional-assertion class ruled DEAD
  after 4 delta rounds; full record in
  docs/process_traces/2026-08-07-plan-factory/PROSE-ESCALATION.md.
  Ready to receive alpha numbers.
- **A1 trust** @ 97fd4c1 (registration-at-read core BANKED; round 1
  early-returned on two authority conflicts). F1/F2 RULED + custodied
  (`RULING-CONSULT.md`, main `fe85b09`): reduce.py reverts (pin
  senior), path-capability registration, content-addressed custody
  store. **Round 2 IN FLIGHT** (out `SP/trust2-out.md`, 8h cap,
  7-step sequence; step-3 diff checkpoints to trust2-commit1.diff).
  Then 16-question delta → gate → merge lifts MINT BAR.
- **A2 recovery** @ b0c8f6d (four elements BANKED, suite 2763 OK;
  arming blocker held open on witness gap). 71-code census; WITNESS-
  SCOPE-RULING custodied (main `6981d2b`): corruption construction
  legitimate, witness_class tri-state, per-class executed-witness
  gates. **Witness round 3 IN FLIGHT** (out `SP/recovery3-out.md`, 8h
  cap, family-checkpoint resumable). Then gauntlet → integration-tree
  post-trust → merge discharges ARMING BLOCKER.
- **A6 U2** @ 5b00200 — **FROZEN at attestation count 3 (cold-gate
  item; U2-FROZEN-COUNT3.md).** Envelope rework + gauntlet fix + the
  enrollment attestation rework all landed on the branch, but the delta
  ruled the attestation-binding class same-signature YES a THIRD time:
  the enrollment registry was auto-generated with always-true verifiers
  (Potemkin), so a ledger-absent epoch_catalog entry passed every layer.
  Per rule-11 escalation discipline, this is NOT answered with another
  loop fix — U2 is frozen pending a deliberate cold gate (fresh
  instance, mechanical packet), schedulable POST-WINDOW. **Freeze costs
  the paper nothing:** U2 issuance was already gated behind Q12 (open) +
  the third convening (not held); the issued D-079 artifact governs
  alpha/beta/gamma. Sound-and-landed (preserve on resume): trigger-set
  recomputation, the 4 non-class closures, the 5-ID resolution test,
  the clean integration merge, all must-not-change items. Resolution
  packet is written in U2-FROZEN-COUNT3.md §"What a resolution must
  establish".
- **D-126 minted** (`1a1dac0`); prose merge `1e6fa16`; ruling commits
  `fe85b09`, `6981d2b` — all pushed.
- If a stream's process dies, the WORKTREE DIFF is the artifact —
  harvest, never re-run blind (codex-run-v3 --resume for died
  workspace-write runs). A3 (CH-1) queued after A2; A4 (estimator) +
  A5 (U11 tool) queued after A1 merges. Same-signature counters live:
  trust relocation classes (delta grades vs 16-question checklist);
  recovery witness-coverage (first occurrence, honest); U2 attestation
  class count 2 (consult-shaped rework in flight — if its delta finds
  the class again, that is count 3 at the enrollment level: cold-gate
  territory, not another fix).

## ▶ MORNING STATE 2026-08-08 (overnight run complete — READ THIS FIRST)

**The night in one breath:** PR #116 merged early (reason-code
diagnostics, full 12-item gate). After that the gates got STRICTER than
the code: THREE standing escalation triggers fired (trust
regression/scoping classes; recovery ungoverned-refusal class across
layers), each redirected to a design consult, and all three consults
returned TERMINATING designs that are now ADOPTED and custodied. The
U2 cold gate re-convened on a workflow-assembled, byte-verified packet
and ruled: six first-round objections verified moot; Q1+Q13 remanded
and then DESIGNED (lineage-monotone envelopes); Q8 shim deleted. The
common-mode estimator (D-124) and the attribution question are settled
with evidence. Nothing unsound merged; the mint bar and arming blocker
correctly stayed up.

**ED'S MORNING REVIEW (reversible items, newest first):**
1. **Q1+Q13 envelope adoption** (Q1Q13-REMAND-CONSULT.md): successor
   screen/ceiling become lineage-monotone t-family envelopes inheriting
   0.010818 as the floor (can only strengthen). The D-117 cl.1
   successor amendment transcribes only with your ack; until then
   freeze-until-ruled controls (costless for the three nights).
2. **D-124** common-mode contrast estimator (two-shared-edge), 4-5x
   floor improvement on contrasts, full registration conditions.
3. Your own D-122 (256-tok prefill arm) + D-123 (reported-energy cells,
   signal-size doctrine) as transcribed — check the wording.

**SUCCESSOR QUEUE (all designs adopted; execution + full gates):**
1. **Trust rework** (registration-at-read; 2026-08-08-trust-scoping-
   escalation/CONSULT-RESPONSE.md): strict-read session, traversal
   deleted, decisive regression replaced on the real-fixture
   no-substitution contract → gate → MERGE LIFTS THE MINT BAR.
2. **Recovery integrated round** (2026-08-08-recovery-exits-
   escalation/CONSULT-RESPONSE.md): stable claim + held lease,
   under-lease ARM readiness, registry-at-raise with executed
   witnesses, §5/§6/§10 runbook amendments → gate → merge DISCHARGES
   THE ARMING BLOCKER (only when all four elements land together).
3. **U2 rework round 2** (SYNTHESIS-V2.md + Q1Q13 consult): envelope
   arithmetic, shim delete, Q5 closure plumbing, Q4 freeze test,
   Q3 evidence regeneration (the lead's 40-digit grid bug), Q13
   refusal rename → re-present Q12 on the FULL register text.
4. **U5-U7 packs:** Ed rulings 2+4 are IN HAND (D-122/D-123) — packs
   generate + freeze once recovery lands (receipt-oracle re-derivation)
   with reported-energy cells, the 256-tok prefill arm, stage_launch
   recipes, and the D-124 estimator identity if its registration lands.
5. Operator packet refresh + results-prose re-run + paper touch-ups
   (D-122 scope wording is already magistrate territory under D-119).

**In-flight at close: NOTHING.** All Sol runs harvested; all agents
returned; caffeinate dies with the session. Scratchpad worktrees
trust/recovery/u2rework remain (branches pushed; safe to lose).

## ▶ SUCCESSOR SCRIPT (2026-08-08 wrap — start here)

**OVERNIGHT RUN LIVE (D-123 license):** rulings D-122/D-123 transcribed;
attribution debate adopted (means: signal-sizing only; contrasts:
common-mode estimator replay ORDERED pre-freeze, promotion bar >=2x/2J).
OVERNIGHT, LATER (state at ~03:30): **U2 second convening RULED**
(SYNTHESIS-V2.md, both sealed rulings custodied): six first-round
objections verified moot in code by BOTH judges; Q5 closure defined and
adopted; Q8 migration shim deleted by convergent ruling; Q9 barrier
verified mechanical; **Q1+Q13 jointly REMANDED to design** (the
refuter PROVED the range-based successor screen crosses the shrinking
t-ceiling at ~67% at the actual n=30 first-successor corpus — silent
clamp + incoherent runtime refusal; consult IN FLIGHT
`<scratchpad>/q1q13-consult-out.md`); Q12 open (the packet truncated
the register AGAIN one paragraph later — packet rule hardened:
quote to end of document section); Q10 defers to recovery. **RECOVERY:
escalation FIRED at count 2 ACROSS LAYERS**
(docs/process_traces/2026-08-08-recovery-exits-escalation/ESCALATION.md
— the Opus lens PROVED by executed probes that the writer's
per-process claim_id wedges the night permanently after the design's
own canonical crash, all three governed exits non-functional; runbook
amendment sits under a not-in-force banner). No fix round 2;
exit-completeness design consult IN FLIGHT
(`<scratchpad>/exits-consult-out.md`). The recovery branch's custody
core is CLEAN (no path admits a control receipt as evidence) — the
class lives in the operator/liveness layer. TRUST: delta4 FAILED — both
round-3 classes at COUNT 2 (regression still substitutes the
production chain; strict-parse both under- and over-scans) → the
trigger FIRED here too
(docs/process_traces/2026-08-08-trust-scoping-escalation/ESCALATION.md);
registration-at-read consult IN FLIGHT
(`<scratchpad>/trust-scoping-consult-out.md`). The custody-authority
class stays DEAD; the MINT BAR STAYS UP tonight — the trust merge
waits for the consult-shaped rework + full gate. THREE consults now
in flight (exits, q1q13, trust-scoping): the night's remaining spend
is consult-harvest -> terminating-shape reworks, not fix-round churn.

OVERNIGHT PROGRESS: trust tripwire delta RULED **same-signature NO —
the operator-authored-authority class is DEAD** (authority terminates in
authenticated ledger/session evidence, committed head pin, code-pinned
D-079 acceptance, authenticated campaign evidence, extractor
recomputation); FAIL only on two first-occurrence items (decisive
regression bypasses the file-backed production entry; strict-parse
over-scans unreferenced files) → **fix round 3 in flight**
(`<scratchpad>/trust-fix3-out.md`; lead replay at fix-2 head banked:
2747 OK unpiped). Recovery audit **FAIL — all three historical classes
found alive as implementation misses** (bare-business-receipt admission
after activation; junk+orphaned-finalization deletion-only state;
count-only pin check; abandonment-head pin rejection; two
non-discriminating test findings; two fixture-discipline P2s) → **fix
round 1 in flight with dictated closures**
(`<scratchpad>/recovery-fix-out.md`); ITS delta is a tripwire: any
class alive again = count 2 = consult. Common-mode replay: bar HELD
decisively → **D-124** (two-shared-edge estimator promoted-as-candidate,
Ed-reversible). U2 exhibit rework still in flight. A `caffeinate -i -m`
(pid recorded in session log, 12h cap) holds the LOCKED machine awake —
it dies with the session; if a future QUIET WINDOW ever finds a stray
caffeinate, kill it before arming. Workflow tool re-authorized by Ed
for tonight at magistrate discretion.

**MERGED this window (all on main):** PR #114 (paper trust language),
PR #115 (U1 night fixes — F2 fixed on main), PR #116 (reason-code
plumbing — FIRST merge under the full 12-item D-121 gate). Decisions
minted: D-119 (claim language), D-120 (trust closure), **D-121 (the
magistrate's OWN contextual final review is the TERMINAL merge-gate
item — binds every merge, non-delegable, after CI)**. Council record:
C-050. Skill-usage log updated.

**TWO SOL RUNS WERE IN FLIGHT at wrap** (background processes die with
the session; the WORKTREE DIFF on disk is then the artifact — harvest,
never re-run blind):
1. **Trust fix round 2** — worktree `<session-377d…>/scratchpad/trust`,
   branch `impl/d117-postcollection-trust` (last pushed head `4fcb687`;
   Sol was editing uncommitted on top). Contract:
   `<scratchpad>/trust-fix-prompt.md`; report (if finished):
   `<scratchpad>/trust-fix-out.md`. It closes the round-1 audit FAIL
   (A1 window-anchor-from-verdict; A2 production-path decisive
   regression; A3 recursive strict-parse; A4 head-pin-commit
   containment). **On harvest: fresh delta re-audit — if the
   operator-authored-authority class survives in ANY form, that is
   same-signature COUNT 2 and the next spend is an ESCALATION CONSULT,
   never a round-3 fix.** Then replay -> PR -> CI -> D-121 terminal
   review -> merge. The v2 mint bar lifts only then.
2. **Recovery resume** — worktree `<session-377d…>/scratchpad/recovery`,
   branch `impl/d117-ledger-recovery` (nothing pushed yet; round 1
   returned NEEDS_SCOPE, magistrate approved expansion to the two
   positional fixture sets with derived-count discipline). Report
   appends to `<scratchpad>/recovery-out.md`. On harvest: commit
   ungated -> full D-118/D-121 gauntlet -> PR. **Its receipt-cadence
   change (5->10 per session) makes the U5-U7 '5-receipt/91' oracles
   STALE — pack generation must re-derive from this branch, and packs
   stay unfrozen anyway pending Ed ruling 2.**

Session scratchpad root:
`/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad`
(prompts, all Sol outputs, worktrees trust/recovery/reasoncode/split†;
† split worktree pruned post-merge). If the scratchpad is gone, the
pushed branches + the prompt texts recorded in `.codex-bridge/` and the
v3 manifests reconstruct everything.

**THEN the queue (unchanged order):** trust merge (mint-bar lift) ->
recovery gauntlet (discharges the night-1 arming blocker via its
runbook amendment) -> U2 packet reassembly + rework (per
`2026-08-07-u2-coldgate/SYNTHESIS.md`) -> U5-U7 pack generation on Ed
ruling 2 (with re-derived receipt oracles + the adopted stage_launch.v1
contract + U11 projection receipts before any ARM).

**ED'S RULINGS OWED: still the 8** (docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md);
ruling 2 is the only pack-freeze blocker; ruling 8 gates the
reason-code SPEC lane (the code lane merged).

## ✅ CHECKPOINT 2026-08-07 EVENING — 3.5h magistrate window (READ THIS FIRST)

### D-121 ERA (Ed directive, 2026-08-08 ~late) + second extension

- **D-121 RATIFIED and transcribed** (decision log + memory): the
  magistrate's OWN contextual final review is the TERMINAL merge-gate
  item (D-118 item 12) — after every other pass INCLUDING CI,
  non-delegable; subagent Fable passes count only as earlier items.
- **Reasoncode: PR #116 MERGED** under the FULL 12-item D-121 gate
  (CI 11/11; magistrate terminal review PASS at `fc93ec1`, recorded in
  the PR ledger). The reason-code plumbing is ON MAIN for the three
  nights; only the spec-ratification lane (Ed ruling 8 + S1-domain +
  SF2 waiver code) remains. Original status line:** Fix round
  1 landed (`fc93ec1`): degrade-not-raise on the emitter (the crash was
  REACHABLE under producer drift — delta proved a synthetic drift case
  crashed the parent), discriminating dedup regression, whitespace
  aligned, dead regex pruned. Delta: ACCEPT, same-signature NO. Full
  replay 2747 OK unpiped. Remaining: CI (watcher armed) → **D-121
  magistrate terminal review → merge**. Opus SF2 (waiver reason code)
  deferred by design to the spec-ratification lane.
- **Trust: adversarial audit round 1 = FAIL, same-signature YES** — the
  operator-authored-authority class survives at ONE site the memo
  already answered: the supplied binding chooses its own window; the
  authenticated VERDICT's bracket must anchor window identity (memo §3).
  Plus: decisive regression not production-path (memo §8), recursive
  JSON not strict-parsed, containment field measures the mint HEAD not
  the head-pin commit (adjudication consequence 2). **Fix round 2 IN
  FLIGHT** (Sol xhigh, contract at `<scratchpad>/trust-fix-prompt.md`,
  report to `<scratchpad>/trust-fix-out.md`). IF ITS DELTA STILL FINDS
  THE CLASS: same-signature at count 2 → ESCALATION CONSULT, mandatory,
  no round 3. Then: fresh delta → replay → PR → CI → D-121 terminal
  review → merge; the v2 mint bar lifts only then.
- **Recovery implementation: round 1 returned NEEDS_SCOPE (correct
  early-return)** — the adopted intent protocol inherently DOUBLES the
  physical receipt cadence (every business receipt gains a durable
  intent receipt; a five-operation bracket session becomes ten
  physical receipts), breaking two out-of-scope positional fixture
  sets (U4's live-three-window regression and a bracketing fixture).
  **Magistrate ruled: cadence change is a consequence of the ADOPTED
  design, not a defect; scope expansion APPROVED for both test files
  with derived-count discipline (no positional hard-coding — the U4
  amendments' own rule). Resume in flight**
  (`<scratchpad>/recovery-resume-launch.log`, report appends to
  `recovery-out.md`). **BINDING DOWNSTREAM NOTE: the '5-receipt/91'
  oracle the U5-U7 pack plans re-derived is STALE once recovery lands —
  pack generation must re-derive receipt-model oracles from the
  recovery branch (packs are unfrozen pending Ed ruling 2, so no
  regeneration cost if sequenced recovery-first).**

### EXTENDED WINDOW (+90min, same evening) — trust + reasoncode gauntlets advanced; three Sol streams in flight at final close

- **Trust branch (`impl/d117-postcollection-trust`) @ `4fcb687`, pushed:**
  integration-merged with post-#115 main (2745 full-suite OK unpiped,
  lead-run); Opus counter-review DONE: PASS-WITH-SHOULD-FIX, no
  blockers, deletion complete, #115 seam clean, assurance qualifier
  byte-exact. Fix round 1 APPLIED at the bench: paper §5/§11 corrected
  (branch had falsified the "mint does not run git" sentence);
  origin/main containment records unknown instead of refusing; field
  renamed `mint_commit_contained_in_origin_main` with a PROVEN golden
  fixture-review (reverse-rename byte-reproduces every old golden on
  synthetic AND CLI paths; cascaded producer pins/set re-derived);
  dirty-tree refusal names paths; **D-120 transcribed on the branch**
  (index row + body; docs tests green). **OWED before PR/merge:**
  harvest `<scratchpad>/trust-audit-out.md` (Sol adversarial per-field
  authority walk, IN FLIGHT at close — it gates everything), fix-round
  delta over `049df4b..4fcb687`, final-head pass, full replay at head,
  CI. Deferred with record (counter-review S4/S6/N1-N3): opaque
  binding-refusal message, labelled-floor profile coverage, allowance
  nit, terminal-head fallback nit, duplicated literal nit.
- **Reasoncode branch:** Opus counter-review DONE: PASS-WITH-SHOULD-FIX,
  no blockers — identity seam PROVEN byte-equivalent (20k-row fuzz, 0
  mismatches), round-trip exact (30k emissions). SF1 (producer-union
  subset test — uncaught ValueError could suppress a verdict row if the
  frozen tuple drifts) + SF2 (waived members invisible in the new
  surface) + 4 nits NOT yet applied — they are the successor's fix
  round, with `<scratchpad>/reasoncode-audit-out.md` (Sol audit, IN
  FLIGHT at close) to fold in. Lead full replay: `<scratchpad>/reasoncode-lead-replay.log`.
- **Recovery implementation** (`impl/d117-ledger-recovery`, worktree
  `<scratchpad>/recovery`): Sol xhigh IN FLIGHT at close implementing
  the adopted ledger-resident intent/finalize/abandon shape incl. the
  runbook D-117 amendment (which discharges the arming blocker).
  Report lands at `<scratchpad>/recovery-out.md`; if the process died,
  the worktree diff is the artifact — commit ungated + gauntlet.


**Executed this window (all pushed):** resume items 1, 2 (both
consults), 3, and 5 of the /clear checkpoint, plus the reason-code code
lane and two U5-U7 amendment closures.

1. **PR #114 MERGED** (`a6bb14f`) — full D-118 ledger: round-1 delta
   FAIL (2 blockers: unqualified tamper/detectability claims) → fix
   `b0ee307` (D-119 conservative qualifiers + plain-language
   mint/pinset/ledger-head-pin definitions) → delta ACCEPT + Fable
   final-head PASS + CI green. Paper custody language is now fully
   aligned with the adjudicated trust model.
2. **Recovery-shape escalation consult DONE + ADOPTED**
   (`docs/process_traces/2026-08-07-d117-u-units/RECOVERY-SHAPE-CONSULT.md`):
   DELETE the sidecar journal; ledger-resident intent/finalize/abandon
   receipts; F1 reborn as ledger-only recovery; three rounds of sidecar
   work discarded. Implementation = NEW work order, full gauntlet,
   sequenced AFTER PR #115 merges (shared calibration_ledger.py).
3. **U1 BRANCH SPLIT EXECUTED → PR #115 MERGED (post-checkpoint
   update: the gate COMPLETED in-session — fix-round delta ACCEPT with
   same-signature NO at count 1, lead post-fix replay 2738 OK unpiped,
   independent Fable final-head PASS on `86d7f59`, CI 11/11; merged
   under D-072 on the full 11-item ledger). F2 is FIXED ON MAIN. The
   ARMING blocker below still stands. Original checkpoint text for the
   record:**
   Port proven pure-subset of 880b6bc; two independent lenses (Sol
   delta + Opus counter-review) convergently caught a REAL P1 beyond
   the original delta (one-sided session endpoint served unbound) →
   bench fix `86d7f59` + discriminating regression (41 focused OK,
   mutation-checked). **OWED before merge (successor's FIRST move):
   harvest `<scratchpad>/split-delta2-out.md` (fix-round delta,
   in flight at close) + `<scratchpad>/split-postfix-replay.log`
   (full unpiped replay, in flight) + final-head pass on `86d7f59` +
   CI → then D-072 merge.** Same-signature: F2 scoping class at count
   1; if the delta2 says "count 2" the escalation trigger fires —
   consult, never round 3. ARMING blocker recorded (not merge): the
   escalation's promised operator runbook procedure for the held F1
   recovery gap is still unwritten.
4. **U2 COLD GATE CONVENED AND RULED: NOT RATIFIED — packet remanded**
   (`docs/process_traces/2026-08-07-u2-coldgate/SYNTHESIS.md` +
   both sealed rulings custodied). Decisive: the packet quoted
   D-102/D-116 while the exhibit's own decision-ID tuple declares
   D-102/D-109/D-117 — D-109 is operative for 7 of 12 questions.
   Convergent technical blockers bind the U2 rework (Q2 screen source,
   Q3 kernel verification, Q11 fabricated successor_probe, Q6
   abandoned-row brick, Q9 publication barrier, Q4 undisclosed one-way
   door, allowance-rule as new Q13). New packet rule: quote every entry
   the exhibit itself declares as authority, diffed mechanically.
   Charter erratum #2: worktree convening does NOT suppress harness
   injection for Agent-tool subagents — disclosure line is the control.
5. **U5-U7 amendments 3+4 CLOSED:** U11 arm-time identity-pin
   projection work order registered
   (`WORK-ORDER-U11-IDPIN-PROJECTION.md`); launch-command contract
   adopted (`docs/process_traces/2026-08-07-plan-factory/PACK-LAUNCH-CONTRACT-CONSULT.md`
   — typed stage_launch.v1 recipes in plan_tree nodes, U8 materializes
   to exact argv). **Pack generation now blocks ONLY on Ed ruling 2
   (reported-energy cells) for the hash freeze**; amendments 1/2/5 are
   generation-time work.
6. **Reason-code CODE lane implemented** (magistrate ruling A split) —
   branch `impl/d117-reasoncode-plumbing` (`21991f1`, pushed),
   self-labeled UNGATED: top-level sibling field both whole-window
   emitters, outside-S1 frozen namespace, golden characterization
   sha256, projection key-list freeze test. **D-118 gauntlet owed
   before any PR.** Spec ratification lane untouched (Ed ruling 8 /
   S1-domain question remains).

**IN FLIGHT AT CLOSE (harvest, do not re-run):**
- **D117-POSTCOLLECTION-TRUST-01: HARVESTED at close** — Sol xhigh run
  came back CLEAN/complete (full suite OK in-run, scope passed);
  committed UNGATED as `impl/d117-postcollection-trust` @ `1b1e500`
  (pushed; 10 files, +1671/-543, incl. the production-path golden
  fixture). **D-118 gauntlet owed before any PR; the v2 mint stays
  BARRED until this lands gated.** Report custodied at
  `<scratchpad>/trust-out.md`. Note for the gauntlet: this branch
  touches calibration_bracketing.py + its tests, as does PR #115 —
  integration-tree the pair before whichever merges second.
- **PR #115 fix-round delta + full replay** (item 3 above).
- Session scratchpad: `/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad`
  (worktrees split/trust/reasoncode live there; prompts + all Sol
  outputs custodied there; bridge audit rows in .codex-bridge/).

**LEAD ERRORS this window (recorded, closed structurally):** (a) an
Opus review subagent launched in the main-repo cwd detached the main
tree via checkout; a bookkeeping commit landed on the detached lineage
and its push silently no-opped — recovered by cherry-pick (`a64f6ad`).
RULE: review agents get isolation:worktree or an explicit no-checkout
line; check `git branch --show-current` before any main-tree commit.
(b) The lead's first full-suite replay was PIPED (tail ate the exit
code) — the twice-recorded rule recurred; replay redone unpiped.

**Ed's rulings owed: UNCHANGED 8** (ADJUDICATION.md) — ruling 2 is now
the ONLY blocker on U5 pack-hash freeze; ruling 8 (refusal-scope spec
governance) gates the reason-code spec lane.

**Successor's order (updated post-merge): (1) trust gauntlet → PR
(branch `impl/d117-postcollection-trust` @ 1b1e500; NOTE it pre-dates
PR #115's bracketing changes — integration-tree before merge); (2)
reasoncode gauntlet → PR; (3) recovery-shape implementation (PR #115
is merged, surface is free) + the owed runbook manual-recovery
procedure (ARMING blocker); (4) U2 packet reassembly + rework; (5)
packs on Ed ruling 2.**

**THE GOAL MAP:** `docs/strategy/HORIZONS.md` — H0 ship the capstone
paper (current focus, everything waits on it) / H1 the ICPE version /
H2 mechanism-level energy (Ed's original research goals, with each axis
honestly statused) / H3 what the instrument could become. Ed points at a
horizon; the magistrate picks the next unblocked move inside it.
Claim WORDING is magistrate territory now, conservative by default
(D-119); what to measure, fund, and scope stays Ed's.


**Nothing in flight. No orphaned processes. Everything pushed.** All
scratchpad worktrees are clean and their branches pushed; they are safe
to lose (recreate with `git worktree add` from the branch names below).

### STATE IN ONE BREATH

Ed's MVP capstone paper draft is COMPLETE and merged (PR #110). Three
D-117 toolchain units merged (U1/U3/U4; PRs #111/#112/#113) and merged
main is lead-verified GREEN (**2733 tests, exit 0, unpiped**). A
retroactive apex-gate pass over those merges then found five real
defects, produced **two escalations that are now the top of the queue**,
and produced **D-118** (nothing merges without the full enumerated
council gate). Ed owes 8 rulings. No quiet night can be armed yet.

### IMMEDIATE RESUME ORDER

1. **EXECUTE THE BRANCH SPLIT** (ruled, not yet done — record:
   `docs/process_traces/2026-08-07-d117-u-units/ESCALATION-U1-RECOVERY.md`).
   Branch `impl/d117-u1-gate-debt` contains BOTH night-critical fixes and
   an escalated subsystem. Land **F2 / F4 / F5 / F6a** (delta-verified
   clean; F2 is a night-critical correctness defect live on main right
   now — the first finalized bracket session silently makes bindings
   mandatory for EVERY historical window). **HOLD F1 + the recovery
   hardening** pending the consult below. Then PR with a complete D-118
   gate ledger.
2. **RUN THE TWO QUEUED CONSULTS** (both are escalations; a further fix
   round on either is FORBIDDEN):
   - *Append-recovery subsystem shape* — three rounds, three distinct
     defects, class still alive (positive-prefix foreign-journal replay)
     plus a refused state with no governed operator exit. Charge is
     written in ESCALATION-U1-RECOVERY.md.
   - *D117-POSTCOLLECTION-TRUST-01* — already consulted and the SHAPE IS
     ADOPTED (delete `floor_mint_postcollection`; rederive every pinned
     value from its domain owner). This one needs IMPLEMENTATION, not
     another consult. It is a pre-window work order and a dependency of
     U10. **The v2 mint is BARRED from issuing until it lands.**
3. **PR #114 (paper trust-model narrowing) — owes 2 gate items** (delta
   re-audit + final-head pass) and says so in its own gate ledger. Not
   merge-eligible until they run.
4. **U5-U7 campaign packs: GENERATE NOW** (apex-examined
   ACCEPT-WITH-AMENDMENTS; packs correctly firewall the mint bar out of
   their bytes). Apply the 5 amendments in
   `docs/process_traces/2026-08-07-plan-factory/MAGISTRATE-DISPOSITIONS.md`
   — including registering the **UNOWNED night-killer**: nothing charters
   the tool projecting arm-time identity pins, and a wrong projection
   makes clean night data PERMANENTLY unmintable.
5. **U2 cold gate: packet is READY**, not convened —
   `docs/process_traces/2026-08-07-u2-coldgate/` (cold Fable from a
   worktree + Opus contract-lens refuter; 12 tagged decision points).
6. **U8: REWORK, do not land** — its runbook edit would put contradictory
   instructions in front of Ed at 2am (§5B still licenses a retry the
   two-slot session cannot represent).

### ED'S RULINGS OWED (8; full text + recommendations in
`docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md`)

1 Window C night (recommend FUND; §6 otherwise ships with no evidence).
2 Reported-energy cells in alpha/beta — **TIME-CRITICAL, must precede the
U5/U6 pack-hash freeze**. 3 Reason-code plumbing (urgent: only 14/44
refused occurrences have a reconstructable reason). 4 256-tok prefill arm
(recommend NO). 5 Quantization posture. 6 Calendar dates. 7 Artifact
scope + wall-meter vs second unit. 8 The `refusal_scope_spec.md`
governance hole (cites D-083, which is a different ruling; no
decision-log row exists for it).

### BRANCHES (all pushed)

`impl/d117-u1-gate-debt` (split pending) · `impl/d117-u2-successor`
(COLD-GATE EXHIBIT, never a PR) · `impl/d117-u8-readiness` (evidence only,
REWORK) · `impl/paper-trust-model` (PR #114, 2 gate items owed).
Merged today: `impl/d117-u1-ledger-session`, `impl/d117-u3-pinset-v2`,
`impl/d117-u4-regression`, `impl/paper-mvp-complete`.

### WHAT CHANGED IN DOCTRINE TODAY (binds successors)

- **D-118**: the merge gate is enumerated (11 items) and mechanically
  checked by a per-PR GATE LEDGER; any NOT-RUN item blocks merge
  regardless of CI; D-072 self-merge is conditioned on it; a burn license
  never reduces the gate. The apex Fable diff gate MAY be delegated to
  Fable subagents (magistrate adjudicates, never skips).
- **D-117**: three prospective windows replace the historical re-mint.
- Memo literals must be RE-DERIVED from landed branches (the memo's
  3-receipt/85 model was superseded by the landed 5-receipt/91 reality).
- No second-paper work touches the mint/pinset/detection_floor file set
  until U10 closes; kill thresholds are multiples of a PROJECTED floor,
  never joule literals.
- **The floor artifact is OPERATOR-ATTESTED**, not machine-verified
  provenance — adjudicated by two converging apex reviews; the paper's
  custody language was narrowed accordingly (PR #114).

### LEAD ERRORS RECORDED (do not repeat)

Custodied mid-write files as if complete (an examiner reviewed a dead
snapshot). Accepted a delta's headline twice while its qualifiers went
unread (U3's CLEAN, later overturned; U4's three PARTIALs, never ruled).
Merged three PRs before the apex gate existed. All are closed
structurally, not by memory.

## ✅ CHECKPOINT 2026-08-06 late — machine-move stop (resume script)

**Nothing in flight; nothing unpushed after this commit.** All background
jobs harvested; consult custodied; campaign logs sha-verified untouched.

**STATE IN ONE BREATH:** PR #109 merged (`c537386`); first consumption
attempt proved the historical re-mint structurally closed at main (see
AFTERNOON block + `docs/process_traces/2026-08-06-d110-remint-fork/`);
Sol xhigh + magistrate recommend Option 2 (three fresh prospective
windows); **Ed has NOT yet ruled** — he was probing costs when the
session stopped.

**Ed's in-thread directives this exchange (record, not yet decision-log):**
1. **MVP claim scope: "a little more than just decode, at least
   decode/prefill."** Magistrate's proposed shape (not yet Ed-acked):
   prefill FLOOR cells ride both fresh floor windows cheaply; a prefill
   CONTRAST first gets a labelled non-claim desk feasibility check from
   historical diagnostics against the D-078 ~5 J effective bar — if it
   clears, the contrast window grows a prefill ABBA arm; if not, prefill
   floors are claimed, contrast stays decode-only, and the infeasibility
   becomes a limitations paragraph.
2. **Ed challenged the zero-agent window rule** ("why can't you be
   running quietly?"). Owed answer components, for the successor: (a)
   physics at our bar — a bursty resident agent stack at ~0.1–0.5 W over
   minute-scale members is joules-to-tens-of-joules gross vs a ~5 J
   effective bar; idle subtraction cancels only the steady part; every
   CLAIM window to date was zero-agent; the app-resident mode was only
   ever used for fenced NON-claim characterization. (b) The banked
   `runs_char_t3appup_20260804_r01/_r02` captures exist precisely to
   QUANTIFY the dormant-app delta — **desk analysis queued (protocol
   §Analysis: mean/p95 package power from rich_telemetry_idle.jsonl)**;
   run it and give Ed a NUMBER. (c) The honest reframe: the binding
   presence constraint is §5A's sudo (network-time toggle), not the
   zero-agent rule; the agent-armed window design (QUIET-GUARD two-phase
   handoff, commits 2–4 + a scoped sudoers rule for the two systemsetup
   commands) exists and was descoped by Ed's OWN ruling as not worth the
   security-critical code — reopenable on his word if three fresh
   windows change his calculus.
3. Ed confirmed understanding that Option 2 = recollect the science
   windows (~3 windows, bookend-presence only) while everything else
   (instrument arc, acceptance rule, tooling, process record) stands.

**RESUME ORDER for the successor:**
1. If Ed has ruled the fork → transcribe the decision (supersede/amend
   D-110 + D-113 rewire per SYNTHESIS.md) and start the Option-2 desk
   queue (AFTERNOON block bottom). If not ruled → he owes: fork ruling,
   prefill-contrast shape ack, three-nights scheduling.
2. T3-CHAR-PAIR r01/r02 desk analysis (the dormant-app number) — cheap,
   answers his live question, informs any zero-agent-rule revisit.
3. Prefill-contrast feasibility desk check from historical diagnostics
   (labelled, non-claim).
4. End-of-session bookkeeping STILL OWED from the marathon session:
   consistency sweep, council log, skill-usage log.

## ⏳ 2026-08-06 AFTERNOON — re-mint fork: historical consumption is closed at main; Ed's ruling owed

**PR #109 merged on green** under D-072 at the gate-reviewed head
`d85b4f9` (no post-review commits; ledger + custody backup verified
byte-identical to the checkpoint sha before merge). `d079recon`
worktree + local branch pruned. All three D-110 conditions were thereby
satisfied — and the FIRST consumption attempt exposed a structural
block.

**THE FINDING (full record:
`docs/process_traces/2026-08-06-d110-remint-fork/` — DIAGNOSIS,
consult prompt+response, SYNTHESIS):** no historical window (a10,
window-C, old window-D, 7B-floor, contrast — all pre-genesis) can pass
authenticated max-bracket consumption at merged main. The issued ledger
holds only import-marked receipts; candidate discovery excludes imports
by design (CAL-BRACKET arc `63f43a68`, retained through issuance);
future live receipts cannot causally bracket past windows. Every
refusal was fail-closed; campaign logs sha-verified untouched (backups
in `~/JouleWise-window-custody/d110-remint-20260806/log_backups/`).

**Sol xhigh pre-decision consult (run `20260806T165843Z-10884`) +
magistrate CONCUR: Option 2 — supersede the D-110 historical re-mint
with THREE compact prospective windows** (fresh 1.5B decode floor,
fresh 7B decode floor, fresh contrast; each live-bracketed under the
issued regime, ~3 h class each). Chain: historical corpus → issued
acceptance rule → live brackets → prospective floors → contrast.
Option 1 (finite-allowlist historical candidacy) preserved as a
cold-gated contingency only — semantics sketch is in the consult
response. The consult verified all five historical bracket pairs exist
physically (drifts 0.000167–0.003680 s, under the 0.010818 s screen) —
the objection is provenance completeness, not causality.

**ED OWES (his ruling moots a cold gate — apex authority):**
1. Ratify superseding D-110's re-mint order with prospective
   replacement (+ the D-113 dependency rewire the consult flags).
2. MVP claim scope: decode contrast only, or more phase cells?
3. Three quiet-mac nights scheduling appetite (§5A each).

**Desk work unblocked regardless (consult §4, queue for the successor):**
freeze the three window plans + budgets (new immutable identifiers —
"Window D" name is taken); 1.5B decode-only floor plan from the proven
10-absolute/40-null design; generalized mint pinsets w/ per-plan
six-decimal literals (the D-084 literal `7.377086` refuses any
corrected mint under EVERY option — closure is per-plan supply via the
generalized path); freeze extraction specs/order manifests/
evidence-root ids/contrast manifest; synthetic three-window live-ledger
integration regression; D-102 successor-artifact packet; results/
methods prose with placeholders.

**Session ops notes:** verdict/extraction tooling gotchas (relative
`--runs-dir` path-doubling; verdict >2 min; stale `campaign.lock` on a
killed run) are recorded in the trace DIAGNOSIS. End-of-session
bookkeeping (consistency sweep, council log, skill-usage log) still
OWED.

## ✅ CHECKPOINT 2026-08-06 morning — executed by the afternoon session above

**IMMEDIATE RESUME ACTION (one live item):**
1. **PR #109 (`impl/d079-issuance`) — merge on green, then RE-MINT.**
   This PR ISSUES the D-079 calibration acceptance artifact (the
   authentication anchor for all floor-mint claims): D-116, issued
   config (fixture→issued, file sha `316113960c…`), committed head-pin
   (seq 76 / head `08456d50…`), cold-gate custody, + a 5-file test
   reconciliation. It cleared its FULL gauntlet (two rule-11 cold gates,
   adversarial audit + 3 delta rounds, exact-bytes dual cold review,
   zero-regression reconciliation + coverage-preservation audit ACCEPT).
   At checkpoint: CI running. **On green → self-merge under D-072**
   (it's the completed gate shape). If a successor finds it already
   merged, skip to the re-mint.

**THE AUTHORITATIVE LEDGER — do not lose (survives /clear as a file):**
- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis
  chain, **git-ignored** (local custody artifact), sha256
  `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`.
  BACKED UP at `~/JouleWise-window-custody/d079-issuance-20260806/`
  (byte-identical). Deterministic from the custodied inputs
  (`docs/process_traces/2026-08-06-d079-issuance-coldgate/ISSUANCE-*`,
  on the PR branch → main after merge) + raw evidence. The committed
  head-pin (in the config) is the D-109 R1.4 trust anchor; the ledger
  file itself is a custody artifact. **Must stay backed up before the
  re-mint consumes it.**

**THE RE-MINT (task 8, the payoff — next after PR #109):**
- D-110 conditions now ALL satisfied: (a) PR #100, (c) PR #105, (b) THIS
  issuance. MINT-GENERALIZE-01 UNBLOCKED. Next: ONE custody session —
  governed a10 phase-floor extraction
  (`configs/floor_mint/a10_extraction_spec.json`, ~20 min) THEN mint #1
  re-derivation under the corrected selector, embedding the never-zero
  `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3 /
  D-110). Same custody session (FLOOR-BIND-01 fence). Claim-critical →
  full gauntlet. Output: non-empty claims table (CLAIMS_STATUS §1) +
  the labelled a10 phase floors (D-078 cl.11) + the 1.5B-vs-7B decode
  contrast (frozen metric `phase_energy_j.decode`, NOT the 146.73 J
  diagnostic). THIS is the MVP demonstration (Phase 3 measured data).

**AFTER THE RE-MINT:** paper results section (task 12, results C-v +
limitations from the minted numbers) → assemble A+ MVP draft (methods
already on main: `docs/paper/draft-v1.md`).

**This session's landed work (all merged to main + pushed):** PR #102
Codex Fast Mode (`CODEX_SERVICE_TIER=fast`), #103 coldgate validator,
#104 registration batch, #106 ledger-bootstrap infra, #107 QUIET-GUARD
commit 1, #108 issuance consumer; decisions D-113 (Window B terminally
claim-retired), D-115 (quiet-guard Q2 authority), D-116 (D-079 issuance,
on PR #109). Two rule-11 escalation consults (CGV F3 closure, QG census
Option C) — records in `docs/process_traces/`.

**Ed's standing directives this session (all durable — memory + here):**
- **Priority stack (BINDING):** P1 the A+ MVP paper, P2 the ICPE
  version, P3 modularity for future inference-technique research
  questions — P3 SACRIFICED if it costs P1/P2. (memory
  `paper-first-priority-stack`.)
- **Syllabus (advisor Rivoire — JouleSort author, sets the metrology
  bar; memory `advisor-rivoire-joulesort`):** Phase 1 (system) DONE;
  Phase 2 (outline+related-work) DONE (draft-v1 on main); **Phase 3
  (>=1 experimental section WITH measured data) = LIVE TARGET** = the
  re-mint demonstration; Phase 4 full paper.
- **Venue ceiling:** ICPE full research track is the realistic ambitious
  target (best fit + Rivoire's community); top-tier only if a mechanism/
  split research bet lands. Full ranked roadmap:
  `docs/strategy/2026-08-06-impressiveness-roadmap.md`.
- **Wall meter:** D-092 ratified it as claim C8; Yokogawa WT310E (~$2935
  new, ~$1-1.5k used), get Ethernet; BORROW from Rivoire's lab first;
  TWO (one per machine) only for the split-inference stretch (both boxes
  colocating). NOT required for the A+ MVP.
- **Sol effort:** high/xhigh per complexity (cap lifted); Fast Mode
  (2.5x credits) on xhigh via `scripts/codex-bridge` only (codex-run-v3
  does not read it — do not modify Ed's personal wrapper).

**Cleanup for the successor:** one scratchpad worktree remains
(`…/scratchpad/d079recon` on `impl/d079-issuance`) — prune after PR #109
merges. The end-of-session bookkeeping (task 9: consistency sweep,
council log, skill-usage log) is still OWED — do it after the re-mint.
Nothing critical is unpushed; main is clean.

---

Last updated: 2026-08-05 LATE NIGHT — Fable magistrate session resumed
from the NIGHT checkpoint. Read the LATE-NIGHT block first; the NIGHT
and EVENING blocks below it are still-valid history.

## ⏳ 2026-08-05 LATE NIGHT — Fable resume: all 4 audits harvested, D-115 adjudicated, two Sol rounds in flight

**Harvest complete** — all four checkpoint audits finished and are
copied to `.desk/2026-08-05-checkpoint-audits/` (cgv-audit-A/B,
qg-audit-A/B; qg-audit-B's `.status` semantic fields failed to parse but
its report envelope is present, final, and well-formed — wrapper
artifact, noted).

**COLDGATE-VALIDATOR-01** — cgv-audit-B (oversight/prune lens) reframes
F3 entirely: B1 blocker (PASS receipt does not bind the judge to the
validated bytes — post-validation exhibit substitution), S1 fenced-
heading false refusals, S2 --help receipt violation, and a prune
recommendation to DELETE the attestation privacy subsystem F3 lives in
(free-text attestation fields discriminate no registry invariant). Per
the rule-11 escalation trigger, a **Sol design consult is IN FLIGHT**
(read-only, high — rule-10 tier is xhigh, Ed's Sol-HIGH-only directive
controls, deviation recorded) on: closure shape (refuse-all-slashes vs
allowlist vs delete-the-subsystem), B1 scope (in-branch vs CGV-HARDEN-01
sibling row), S1/S2 disposition, regression vectors. Magistrate's
analysis in the consult: the `input / output` acceptance test and the
privacy invariant are mutually unsatisfiable (POSIX filenames may
contain spaces), so no denylist regex can close F3. Consult prompt +
output land in the session scratchpad; do not land the branch before
synthesis.

**QUIET-GUARD-01 commit 1** — both audits FAIL the branch; convergent
blockers: observation-failure conflated with ABSENT → false-zero census
can release custody; `idle` state accepts a live lease; plus init-wedge
(A-F3), installer-as-root-code-loader under cached sudo (B-F3), `-E` is
not isolation (B-F5), pre-landed Commit-2/3 behavior (A-F5), Darwin
decoder has no discriminating coverage (A-F6/B-F6), D-114 marker
collision (A-F4/B-F4). **D-115 ADJUDICATED and pushed to main
(`0941cf5`)**: Q2 setup authority = fixed installation capability, with
binding conditions 2a (sudo -k fresh auth) / 2b (authenticated staged
content) / 2c (real interpreter isolation); numbering collision with the
descope's D-114 resolved (entry lands via main, merged into the branch
at `262faca` — packet-letter deviation ruled and recorded in the entry).
**Sol fix round IN FLIGHT** (workspace-write, high, WRITE_SCOPE = the 8
commit-1 files, decision log excluded) closing all ten findings with
defect-shaped regressions. On return: lead replays tests unpiped, then
DELTA RE-AUDIT (fix rounds introduce defects — proven), then land
commit 1 only.

**Wrapper gotcha rediscovered (add to field notes):** codex-run-v3
takes the prompt as a literal STRING (`"$*"`), not a file path — pass
`"$(cat prompt.md)"`. A file-path arg silently becomes the whole prompt
(and with --write-scope fails rc=64 on the missing WRITE_SCOPE line).
One consult was launched with a path-as-prompt, killed cleanly, and
relaunched before any output was consumed.

**Unchanged queue after these land:** a10 phase-floor extraction, then
MINT-GENERALIZE-01 (b)+(c) — the D-110 re-mint embedding
`max(drift, 0.010818 s)`, clause (c) = last sweep blocker DC-2/FM-3.
Scout correction (this session): the a10 extraction must run in the
SAME custody session as re-mint consumption (FLOOR-BIND-01 fence), so
it sequences with the re-mint, not standalone.

### Overnight progress ledger (updated ~23:50; all evidence in .desk + session scratchpad, custody commits as noted)

- **D-113 TRANSCRIBED + pushed** (`8e68cde`, consult trace in
  process_traces/2026-08-05-d113-rigor-consult/). CLAIMS_STATUS WB
  terminal labels landed this commit; kernel row retirement rides the
  next registration batch.
- **QUIET-GUARD**: fix round 1 closed all ten findings (lead-replayed
  95/95 + full suite green; bench-committed `e0acaf7`); xhigh delta
  re-audit FAILED it (F1 blocker: idempotent init retry can report
  success with unresolved directory-fsync durability; F2 partial-
  upgrade ordering; F3 census availability; F4 evidence gaps) — **fix
  round 2 IN FLIGHT** with lead-dictated closure shapes.
  Same-signature counter: init-durability at 1 (F1 is an introduced
  defect, first fix; trigger fires if the next delta fails there).
- **COLDGATE-VALIDATOR**: consult-adopted restructure landed on the
  branch (`3964c6e`, lead-replayed 26/26 + frozen-packet smoke; suite
  2514 green); xhigh delta re-audit FAILED it (B1: malformed digest
  arg serialized verbatim into REFUSE receipts — live-proved; B2:
  non-CommonMark backtick fence opener lets a phantom fence HIDE real
  duplicate headings → duplicate Charter pin PASSes) — **blocker fix
  round IN FLIGHT**. Fence-parsing same-signature counter: 1.
- **D-079 issuance**: verification COMPLETE (38/38 recovered,
  hash-authenticated, physics-replayed: 32 valid / 6 invalid / 0
  unresolved) but BLOCKED on two items. **B1 RULED by the lead**: the
  two high-bound members (`20260726T000039-491995f3`,
  `20260801T064830-c76f5d1c`) are SYSTEMATIC-INVALID in the ledger
  (production preflight screen + D-102's explicit naming control over
  the candidate tool's stored-status labels; R2.8's "six further" was
  conditioned on the unratified candidate inventory — valid total is
  30, eight further to trigger). **B2 (no deterministic bootstrap
  contract) — design+implement session IN FLIGHT** on
  impl/ledger-bootstrap (xhigh; genesis-only, atomic, import-marked
  receipts, dry-run default; expected head `8e80b6e9…` under the
  report's rules). Verification record custodied:
  process_traces/2026-08-05-d079-issuance/. Issuance itself (execute +
  head-pin commit + artifact edit + D-116 entry) remains a separately
  gated step — Ed pre-authorized overnight, conditional on the gate.
- **Fast-tier**: PR #102 open, CI running; lead-replayed 70/70 incl.
  desktop IPC tests; solo-review ruled proportional (Ed-dictated
  20-line diff). On merge: fast rides scripts/codex-bridge
  (codex-run-v3 does not read CODEX_SERVICE_TIER — do not modify Ed's
  personal wrapper without his word).

### D-079 ISSUANCE HELD by cold gate (recorded ~03:30 2026-08-06) — issuance is IMPLEMENTATION, not an edit

Rule-11 cold gate on the irreversible issuance SPLIT: fresh Fable
instance PROCEED (ledger/head/disposition all verified correct — head
`08456d50…@76` independently reproduced, B1 ruling confirmed vs D-102);
Sol xhigh contract-lens HOLD (two real blockers). Magistrate upholds
HOLD — the gate caught that my issuance packet was underscoped:
- **F1:** `calibration_bracketing.py` has NO consumer path for an
  ISSUED acceptance artifact (only the genesis fixture; production
  unconditionally refuses anything else). A JSON flip makes it
  unloadable.
- **F2:** `derivation_sha256` is over the whole artifact core, not just
  n=19 — flipping `artifact_role` changes it `3cece3b2…`→`a0b98acf…`
  (lead-reproduced). "n=19 preserved ⇒ digest preserved" is FALSE.
- F3: real ledger path is `runs/calibration_observation_ledger.jsonl`.
  F4: all 38 custody locators are iCloud (packet said 22).
Full synthesis + both verdicts custodied:
`docs/process_traces/2026-08-06-d079-issuance-coldgate/`.
**Issuance now = a design-bearing consumer implementation** (issued-
artifact loader authenticating cutoff vs the committed ledger head +
prefix; deterministic issued-artifact emission with recomputed digest)
→ gauntlet → re-cold-review of exact final bytes → THEN the irreversible
`--execute` → D-116. The re-mint (task 8) stays blocked on issuance
COMPLETING. D-110(c) is landed (PR #105); Sol's "not on main" was wrong.
**This is the gate working: it prevented an irreversible ledger write
paired with a production-refused artifact.**

### GOVERNING PRIORITY STACK (Ed, 2026-08-06) — all work serves the paper
P1 the A+ MVP paper; P2 the long-term ICPE version; P3 modularity to
answer the future inference-technique research questions (spec decode,
MTP, MoE, KDA, split) — kept where FREE, but SACRIFICED if it costs P1
or P2. Decision rule for every design choice: serve MVP → ICPE → keep
the future-axis seam modular only at no cost to 1&2; else ship. Do not
gold-plate future-axis machinery before the paper is secured. (Memory:
`paper-first-priority-stack`; refines `modularity-preference`.)

### SYLLABUS ANCHOR (Ed, 2026-08-06) — the overarching goal
Phase 1: develop/justify/demonstrate an LLM-inference energy measurement
system — SUBSTANTIALLY DONE (repaired+validated instrument; metrology
framing). Phase 2: detailed CSCSU paper outline + related-work draft —
DONE (outline v1 + related_work_draft.md). **Phase 3 (LIVE TARGET):
draft >=1 experimental section INCLUDING MEASURED DATA** — this is the
re-mint's phase-floor/contrast output; issuance→re-mint is the critical
path to it. Phase 4: draft the full paper. Front-load the issuance→
re-mint chain and the experimental-section draft above all else.

### QG census — magistrate stop-condition set (recorded ~02:40 2026-08-06)

The Option C redesign delta audit (qg-deltaC, xhigh) found the
observation/churn-to-absence class SURVIVES — but the survival is
localized to ONE discriminator clause: `PID_REUSED` fires on any
full-identity mismatch, whereas the adopted consult explicitly requires
"only a different START-TIME anchor may classify as PID_REUSED" (a
same-start exec/argv/ancestry change must REFUSE, not clear custody).
Every STRUCTURAL piece the consult prescribed passed. Magistrate call:
this is a mis-implementation of a sentence the consult already wrote,
not the design being wrong — so ONE precise fix against that clause is
warranted (first occurrence on this specific new logic).
**HARD STOP-CONDITION (binds the magistrate): if the fix's delta audit
still finds the class, the branch is SHELVED for Ed — no further
iteration.** QG commit 1 is descoped, installed-INACTIVE, on no
measurement path, and gates no claim; it does not warrant unbounded
spend, and rigor-first (D-113) governs CLAIM-BEARING collection, not a
convenience guard. This stop-condition is the record of that judgment.

### ESCALATION TRIGGER FIRED — quiet-guard observation-failure→absence class (recorded ~01:15 2026-08-06)

qg-delta3 (xhigh) ruled the class RECURRENT at count 2: round 3's
protected-set fix omitted the lease owner and matched by PID only,
after round 2's retry introduced the class. Per rule 11 the next spend
is a CONSULT — launched (Sol xhigh, read-only) on the closure shape,
with the magistrate's structural diagnosis (protected-set ENUMERATION
is the regenerating failure; Option A = eliminate enumeration,
universally fail-closed retry) and an admission on the record: the
round-2 lead contract seeded the class by dictating "retry for
unrelated pids" (an enumeration concept) to serve an availability
requirement the lead is now prepared to revoke. F2 (lock continuity)
is CLOSED; init-durability remains closed at count 1. The branch does
NOT land until the consult-adopted shape closes the class and a delta
re-audit accepts.

### Ed directive batch (2026-08-05 ~22:00, in-thread; 12-hour autonomous window)

1. **Sol effort cap LIFTED**: high/xhigh per complexity (rule 10
   restored); prior HIGH-only directive retired by its author.
2. **Codex Fast Mode (service tier)**: 1.5x speed / 2.5x credits;
   Ed specified the then-authorized call-scoped setting via
   `CODEX_SERVICE_TIER=fast`, without a standing default — being
   implemented on `impl/codex-fast-tier`. License: use fast on xhigh
   runs by default, fast-on-high when other streams block on the
   result.
3. **D-113 RULED (c) by Ed**: Window B re-evaluation ABANDONED; Window
   C will be collected fresh. Prerogative, Ed verbatim: "the rigor of
   the data collected matters, i have ample time — soundness and
   quality of the project and claims above all." Sol xhigh consult on
   managing that prerogative is in flight; the magistrate transcribes
   D-113 after synthesis.
4. **Acceptance-artifact issuance AUTHORIZED overnight** (MINT-
   GENERALIZE-01 clause (b)), conditional on the D-079 backfill
   verification (in flight) coming back fully resolved and passing the
   lead review gate; full record for Ed's morning review.
5. Workflow/fan-out standing license re-confirmed for this push.

## ✅ CHECKPOINT 2026-08-05 night — Ed model-switch stop (successor is FABLE; read this, then the EVENING queue)

**Why the stop:** Ed hit the auto-mode classifier tier-flap (the
adversarial-audit vocabulary trips it — documented in codex-delegation
§Security) and ordered an ASAP checkpoint so he can resume on Fable.
State is DURABLE: both in-flight branches are PUSHED to origin (ephemeral
worktrees are safe to lose); nothing critical is unpushed.

### What landed this session (pushed; main green at `b55008f`)

- **PR #101 (T3-AMEND-01) MERGED** on green under D-072 (`906ddf9`);
  row retired (`b55008f`, kernel pins 65→64); `impl/t3-amend` worktree +
  branch pruned.
- **Two "open" queue items were verified ALREADY DONE** (stale
  carry-forwards; no work needed):
  1. Voided-number scrub — landed 2026-08-03. README clean;
     PROJECT_STATUS:83 labels 147 J diagnostic + names registered
     141.29 J w/ D-110 caveat (covers DC-1 too); voided a10/7B values
     confined to CLAIMS_STATUS's non-claim-bearing section.
  2. RT-1 — was ADJUDICATED same-day as decision-log **D-110** (mint #1
     tainted; re-mint must embed never-zero `max(drift, 0.010818 s)` per
     D-102 pin 3). Sweep memory `two-week-soundness-sweep-2026-08-03`
     updated to un-stale both.
  Net: of the two-week sweep's four blockers, only **DC-2/FM-3**
  (validator evidence_root_id pin-widening) is live open work — and it
  is exactly MINT-GENERALIZE-01 clause (c).

### IN FLIGHT at checkpoint — harvest, do NOT re-run blind

Four fresh read-only Sol audits (high) were launched over the two
uncommitted-at-EVENING branches, two lenses each. At stop: **cgv-audit-A
DONE; qg-audit-A, qg-audit-B, cgv-audit-B still RUNNING** on their own
2400 s watchdogs (they will finish and write to the session scratchpad —
path in `.desk/2026-08-05-checkpoint-audits/AUDIT-SCRATCHPAD-PATH.txt`;
completed reports + all four prompts copied into that `.desk` dir for
durability; if the scratchpad is gone, the prompts re-run the audits).

1. **COLDGATE-VALIDATOR-01** — branch `impl/coldgate-validator` @
   `38b6570` (PUSHED). Bench tests pass (31, unpiped exit 0).
   **cgv-audit-A verdict = FAIL / F3 PARTIAL (should-fix):** the F3
   "structural closure" commit still lets a **whitespace-leading POSIX
   absolute path** (`--launch-environment-attestation "cwd='/ secret'"`)
   bypass validation + serialization preflight and exit 0 with PASS
   containing the secret (`scripts/validate_gate_packet.py:73,126,607`).
   This is the **THIRD formulation of the same F3 absolute-path-bypass
   signature** → per rule 11's standing escalation trigger the next spend
   is a **CONSULT on the closure shape, NOT fix round 4.** cgv-audit-B
   (oversight/overbuild-prune lens) still pending — read it first; it may
   add prune items. **Do not land this branch until F3 closes via
   consult.**
2. **QUIET-GUARD-01 commit 1** — branch `impl/quiet-guard` @ `d482869`
   (PUSHED, checkpoint commit self-labeled UNAUDITED). Bench tests pass
   (84, unpiped exit 0). Both audits (qg-audit-A delta re-audit of the
   7-blocker fix round whose report was lost; qg-audit-B adversarial
   priv-esc/fail-closed lens) were still RUNNING at stop — **harvest both
   verdicts before landing.** On clean: land **commit 1 ONLY** (quiet
   lease + process census, installed-INACTIVE); commits 2–4 remain
   SHELVED per the EVENING descope.

### Next substantive item (un-gated payoff)

**MINT-GENERALIZE-01 (b) issuance + (c) validator pin-widening** — the
D-110 corrected re-mint; condition (a) satisfied by PR #100. Clause (c)
is the last live sweep blocker (DC-2/FM-3). The re-mint MUST embed the
never-zero `max(drift, 0.010818 s)` allowance (the RT-1/D-110
correction). This is the path back to a non-empty claims table.

### Standing facts unchanged

Sol HIGH only (Ed). Never gate a commit on a piped test command. Rule 11
cold gates convene from a worktree. Ed's parked decisions (D-113/WINB-R06,
window C §5A, NVIDIA) all unchanged.

## ✅ CHECKPOINT 2026-08-05 evening — DESCOPE + RESUME SCRIPT (still-valid queue; NIGHT block above updates it)

**Ed's directive this session (supersedes the 2026-08-03 T3-DRIVE
priority, which was Ed's own and is Ed-reversed): the t3 control-plane
build-out is NOT worth its cost. Get back to the project.** t3 remains
the INTERACTIVE control plane (Ed drives sessions from it, remotely —
free, keep). What is dropped is **t3-resident-during-measurement-
windows**: windows return to the proven zero-agent guarded-shell path
(quit t3 → §5A → walk away), which produced every successful claim
window to date. The Q13 degraded tail (relaunch fails, no remote
signal) is Ed-ACCEPTED as an edge case — a failed relaunch needs
physical presence anyway.

### SUCCESSOR'S QUEUE — start here, all agent-startable desk work

1. **RT-1 mint-floor understatement** + **README/PROJECT_STATUS voided-
   number scrub** — the two open blockers from the 2026-08-03 two-week
   soundness sweep (memory: `two-week-soundness-sweep-2026-08-03`).
2. **a10 phase-floor extraction** — pure desk work, banked since
   2026-07-25 (memory: `joulewise-window-a-claim-path`).
3. **MINT-GENERALIZE-01 (A12)** — **D-110 condition (a) is SATISFIED**
   as of PR #100 (merged today, `f75d12b`). Remaining: (b) acceptance-
   artifact issuance and (c) validator pin-widening — both desk work,
   now un-gated. This is the path back to a non-empty claims table.
4. Then the D-095 chain / gated contrast claim.

**Ed-gated, unchanged, not blocking:** window C (needs a fresh §5A
physical); **D-113 / WINB-R06-DISPOSITION-01** (biggest parked
decision); NVIDIA ratification.

### What landed this session (all pushed; main green)

- **PR #100 MERGED** (`f75d12b`) — CAL-BRACKET-D079-01 / D-109. Row
  retired, kernel pins 66→65 (`e160c89`), D-110(a) satisfied.
- **Ed ratification batch** (`3931233`): both cold-gate acks recorded
  (cold-packet-handoff gate CLEARED-WITH-EXCEPTION; charter registry
  **RATIFIED**), QUIET-GUARD Q10/Q13 ruled (both later SUPERSEDED by
  the descope + the credential consult below), council C-048.
- **D-072 mechanical self-merge RESTORED** — `.claude/settings.local.json`
  (untracked, per-machine) now allows `gh pr merge`; the classifier
  block that forced Ed-taps is cured. Memory `merge-authority-with-review`
  updated.
- **PR #101 OPEN → merge on green** — T3-AMEND-01, final delta **ACCEPT
  zero blockers**. Full gauntlet: draft → 2 lenses → fix → delta FAIL
  (2 blockers) → fixes + design consult → ACCEPT. Contract stays
  v1.1; v1.2 bump recorded as a recommendation for a future ratification.

### IN FLIGHT at checkpoint (harvest from disk — do NOT re-run blind)

- **QUIET-GUARD-01 commit 1** — Sol fix round RUNNING at checkpoint
  (`scratchpad/quietguard`, branch `impl/quiet-guard`, work UNCOMMITTED
  in-tree). It closes 7 audit blockers (priv-esc via env-selected
  interpreter; validate/install TOCTOU; arbitrary-root test initializer;
  macOS process identity via `kinfo_proc`/`KERN_PROCARGS2`/ancestry
  recheck; boot/hostname wedge; missing decision entry; tautological
  tests). Report: `scratchpad/qg-fix-out.md` + `.status`. **On harvest:
  replay tests unpiped, delta re-audit, land commit 1 ONLY.**
- **COLDGATE-VALIDATOR-01** — F3 final fix round; worktree
  `scratchpad/cgvalidator` (branch `impl/coldgate-validator`) has
  UNCOMMITTED Sol edits. Needs bench replay + a final delta, then PR.

### DESCOPE — what is SHELVED (do not build; reopen only on Ed's word)

QUIET-GUARD commits **2–4** (t3 handoff chain, resident watcher,
t3-relaunch, README banner projection); **T3-CHAR-PAIR-01** (r03
re-capture AND the app-DOWN arm); **WO-T3-VIS-01**; **SEC5A-REMOTE-01**
(was gated on the guard). QUIET-GUARD-01 is re-scoped to **commit 1
only** — the quiet lease + process census, installed-INACTIVE — which
keeps real non-t3 value: mechanical refuse-at-arm for the ordinary
guarded window launcher, replacing today's procedural eyeballing.
The four Ed-questions from the credential consult are MOOT under the
descope.

### Design record worth keeping (from the credential consult, before descope)

Ed's challenge — "why so much security-critical code for a small
convenience?" — was correct and is the reason for the descope. For the
record if commits 2–4 ever revive: putting a git credential in a
root-owned guard is wrong (a credentialed network pusher DURING a quiet
window contradicts the window's defining property). The right shape is
credentials only at the unprivileged interactive boundary (pre-arm and
post-window pushes), a **pre-armed server-side dead-man alarm** for the
no-return case (also catches total host death), a dedicated non-login
service UID (`_joulewiseguard`) rather than HOME-restore env scrubbing,
and Q10/Q11/Q13/Q19/Q24 revised as a SET. Full consult record in the
session run report.

### Follow-on rows to register (queued this checkpoint)

- **T3-PROV-SCHEMA-01** (P2) — four-axis provenance record +
  `authority_class` + ingestion-event schema. **Contract §8 references
  it by name**: it is what ENDS the §8 transitional convention and
  supplies real reverse-consult enforcement (today the adapter validates
  only self-reported headers — disclosed honestly in §8, with
  consumption-side fail-closed as the actual protection).
- **CGV-HARDEN-01** (P3) — receipt-write TOCTOU (dirfd-relative write)
  + fsync/dir-sync atomicity; both pre-existing, deferred deliberately.
- **codex-bridge sandbox-flag defect** (P2, real) — `scripts/codex-bridge`
  `review` mode records `observer_sandbox=read-only` in its audit
  manifest but never passes `-s read-only`; sessions actually launch
  workspace-write, so the audit metadata MISSTATES enforcement. Caught
  live by a review lens (~line 451-453). Needs the flag + a regression.

### Standing operating facts (unchanged, still binding)

- Sol effort cap **HIGH only** (Ed) — no xhigh without his word; record
  the deviation if a ruled gate composition names higher.
- Never gate a commit on a piped test command (recurred twice).
- Rule 11 cold gates convene **from a worktree** (doctrine provably
  absent there); charter is RATIFIED and hash-pinned.
- **Timeouts are hang insurance, never work budgets** (Ed, this
  session): a TIMEOUT indicts the UNIT SIZE — decompose across Sols,
  never accept it as failure. Folded into codex-delegation §Protocol.
- **The merge gate includes an OVERBUILD PRUNE** (Ed, this session):
  Sol writes too much code/too many tests on occasion; "would I want to
  maintain this diff" is part of the Fable diff gate. Folded into
  operation-loop §4g.
- Delegated prompts forbid touching any audit/state/manifest/log
  artifact — "the trail is not yours to repair."

## ✅ 2026-08-05 — Ed's decision batch executed (PR #100 merged; acks recorded; quiet-guard ruled)

Ed answered the checkpoint's owed decisions in one sitting; this
session executed them:

1. **PR #100 / CAL-BRACKET-D079-01: MERGED** (`f75d12b`, 2026-08-05
   ~17:00 UTC) under D-072 with Ed's explicit go. Row RETIRED from the
   kernel (Completed table has the full evidence cell); **D-110
   re-mint condition (a) is SATISFIED**; MINT-GENERALIZE-01 stays
   blocked on (b) issuance + (c) validator widening; **T3-AMEND-01 is
   UNBLOCKED** (first desk item, per the queue). The T3-DRIVE-PRIORITY
   gate's in-flight exception is spent.
   **Merge plumbing fixed:** Ed added the harness permission rules
   (`gh pr merge`, `gh run *`) to `.claude/settings.local.json` — the
   D-072 standing self-merge authority is MECHANICAL again; "Ed names
   merges" is retired as a forced pattern (Ed can still flag
   Ed-merge-only per the memory note).
2. **Both cold-gate acks RECORDED (Ed, 2026-08-05):** (a) the
   cold-packet-handoff acceptance gate is CLEARED-WITH-EXCEPTION
   jointly with the worktree-launch cure, per the judges' recommended
   disposition; (b) the coldgate charter registry status flipped
   BOOTSTRAP-AUTHORIZED → **RATIFIED**
   (`docs/process/coldgate_charter_registry.md`). Remaining t3
   acceptance gates OPEN: checkpoint-restore, app-death recovery
   (both need Ed present).
3. **QUIET-GUARD-01 Ed rulings banked** (recorded in the spec trace
   `docs/process_traces/2026-08-04-quiet-guard-spec/CONSULT-RECORD.md`):
   Q10 = dedicated guard git identity WITH unattended push licensed;
   Q13 = README status-section projection as the closed_degraded
   channel (rides the Q10 push license; phone push optional later).
   Q2 (state root) and Q3 (launch perimeter) proceed on lead defaults
   subject to Ed veto: one-time sudo setup script for the root-owned
   state dir; lead-drafted perimeter enumeration for Ed confirmation.
   The implementation packet is fully unblocked.
4. **Site-lane fix:** the advisory `site` workflow was failing on main
   (C-048 detailed heading missing from the council-log index table —
   predates the merge); index row added this commit.
5. Still Ed's, unchanged: D-113/WINB-R06 (biggest parked decision),
   the two presence gates + app-DOWN characterization arm (one
   Ed-present sitting), r03 app-UP re-capture needs the app kept
   alive (or waits for QUIET-GUARD), D-080 runner choice, NVIDIA +
   Blacksmith parked.

## ✅ CHECKPOINT 2026-08-04 ~06:30 — Ed-ordered stop (successor script)

**State is CLEAN: nothing in flight, no orphaned processes, all repo
work pushed.** This session (successor magistrate) executed the
handoff's first decision end-to-end:

1. **PR #100 / CAL-BRACKET-D079-01: GATE-COMPLETE, CI GREEN at
   `4280ebd`, MERGE AWAITS ED'S TAP** (harness classifier denies agent
   `gh pr merge`). [MERGED 2026-08-05 `f75d12b` — see the top block.] Full arc: consult → reviewed interface amendment →
   lead integration-tree replay (2487 OK, exit-0 unpiped) → delta
   re-audit (caught a LIVE guard bypass: repr-'None' default spoof) →
   hardening + regression → CI green. Records:
   `docs/process_traces/2026-08-04-calbracket-integration-collision/`
   (FINDING + RESOLUTION + both Sol reports), D-109 addendum II,
   C-048. ON MERGE: retire the row; D-110 re-mint condition (a)
   satisfied; MINT-GENERALIZE-01 stays blocked on (b)+(c).
2. **T3-CHAR-PAIR-01 app-UP arm: 2 of 3 captures BANKED.**
   `runs_char_t3appup_20260804_r01` (~01:59) and `_r02` (~06:1x) both
   `status=succeeded` exit-0 with full raw + `rich_telemetry_idle.jsonl`.
   **r03 is DEAD-PARTIAL** (session process died mid-capture; idle
   plist exists but the run never finished): DELETE the r03 dir and
   re-run `configs/characterization/char-t3appup-r03.json` fresh, then
   do the desk analysis (protocol §Analysis; note the r01-vs-r02/r03
   time-of-day split under limitation 2). TWICE this session a
   `run_in_background` capture loop was killed by the harness process
   exiting — captures that must survive the session need Ed to keep
   the app alive, or the QUIET-GUARD detached-watcher shape (which is
   exactly what QUIET-GUARD-01 builds).
3. **Kernel/bookkeeping current:** TEST-SPEED-01 Phase 1 recorded
   landed (PR #98 merged, worktree+branch pruned); MINT-GENERALIZE-01
   acceptance oracle reworded per the D-110 clarification; RUN_STATE
   stale claims corrected (char captures "collected overnight" was
   FALSE at handoff; byte-frozen framing). gen_state --check clean.
4. **Not started:** QUIET-GUARD-01 implementation packet (agent-lane
   head; spec + 25-question intake ready). Ed's owed items unchanged
   (two acks, two presence-gates incl. app-DOWN arm, D-113/r06,
   D-080 runner, QUIET-GUARD's four questions).
5. Worktrees: `calbracket` (impl/cal-bracket-d079 @ `4280ebd`, PR
   #100) — keep until merge, then remove; tooling-owned ones left
   alone.

The 2026-08-03 T3-CUTOVER block beneath the handoff block holds the
control-plane doctrine as ratified; the 16h-runway block below that
remains the older STREAM-STATE reference.

## ✅ CHECKPOINT 2026-08-04 early AM — T3 HANDOFF (successor script)

**You are the successor magistrate. Ed's standing directive
(2026-08-03 ~23:55): the T3-DRIVE CHAIN OUTRANKS ALL NON-IN-FLIGHT
WORK** — the project's own work is paused until Ed can drive everything
from t3, because that unblocks far more than it costs. This is enforced
mechanically, not by memory: kernel gate `T3-DRIVE-PRIORITY` gates
every lane, and `TASK_QUEUE.md` renders non-allowed rows GATED. Queue
heads: **QUIET-GUARD-01** (agent lane), **T3-CHAR-PAIR-01** (quiet-mac
lane). Scoping limit (Ed, SX5): t3 is the preferred presentation plane
WHEN IN USE, never mandatory — a plain claude-code session carries no
t3 ceremony and must not be polluted with t3 context.

### What landed overnight (all pushed; nothing dangling)

1. **CAL-BRACKET-D079-01 / D-109: through its full gauntlet.**
   **PR #100 open** at `c2f81d4` on `impl/cal-bracket-d079`. Audit
   blocker B1 needed a second fix round → rule-11 cold gate convened
   FIRST (record: `docs/process_traces/2026-08-03-calbracket-b1-gate/`
   — packet, cold Fable judge, Sol refuter, both sealed pre-synthesis,
   plus SYNTHESIS.md as the binding contract). Round 2 landed the ruled
   shape; **delta re-audit CLEAN, zero findings, B1 CLOSED both
   dimensions**; lead replay `Ran 2456 tests OK (skipped=82)` exit-0
   unmasked (closes the TMPDIR gap both prior audits flagged).
   **INTEGRATION COLLISION: RESOLVED 2026-08-04 (successor session) —
   PR #100 is GATE-COMPLETE and CI-GREEN at `4280ebd`; MERGE AWAITS
   ED'S TAP** (the harness classifier denies agent `gh pr merge`; Ed
   names merges). Disposition of record:
   `docs/process_traces/2026-08-04-calbracket-integration-collision/RESOLUTION.md`
   (finding: `FINDING.md` same directory; pre-decision Sol high consult:
   `../2026-08-04-calbracket-collision-consult/`). Shape executed:
   main merged into the branch (`341055e`, remerge-proven clean union) →
   reviewed interface amendment `4c0897a` (the guard's signature pin
   updated to the D-109 core signature; the dishonest "byte-frozen"
   framing renamed to review-pinned mint-core interface; literal
   signature-pin test; snapshot-identity regression) → fresh delta
   re-audit (two should-fixes, no blockers) → guard hardening `4280ebd`
   (the audit PROVED a repr-'None' default spoof passes rendered-
   signature comparison; the guard now identity-checks the None
   sentinel defaults, with a regression). Byte-identity oracle
   CORRECTED per the consult: integration-tree core-vs-wrapper PARITY
   (proven, tests pass), NOT historical mint-1 digest match — D-110's
   corrected re-mint may legitimately differ. Evidence: lead full-suite
   replay on the integration tree `Ran 2487 tests OK (skipped=82)`
   exit-0 unpiped; PR CI fully green at `4280ebd`. ON MERGE: retire the
   row (D-110 re-mint condition (a) satisfied; MINT-GENERALIZE-01
   stays blocked on (b) issuance + (c) validator widening).
   **PROCESS FINDING (fix the habit, not just this branch):** the lead's
   rule-1 replay ran in the BRANCH tree, which cannot execute tests that
   exist only on main. Whenever a branch is behind main, the lead's
   verification replay must run on the INTEGRATION tree — otherwise it
   verifies a tree that will never be merged.
2. **T3-doctrine cold gate: RULED and synthesized.**
   `docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md` is
   the disposition of record. Every question AFFIRMED as amended /
   narrowed / qualified. **Charter v2 RATIFIED** at digest
   `099de884…c95d81` (`docs/process/coldgate_charter.md`; registry =
   `coldgate_charter_registry.md`). Two judges (Ed ran desktop- and
   phone-initiated threads concurrently, by design) + an adverse Sol
   refuter whose 13 findings were each adopted as an amendment,
   answered by custody evidence, or recorded.
   **A BLOCKER both judges raised: charter-suppression FAILED live** —
   cold instances launched in the main checkout receive
   `CLAUDE.local.md` + memory by harness auto-injection. CURE ADOPTED
   in the registry's convening procedure: **convene cold instances from
   a git WORKTREE** (doctrine provably absent there) and require a
   contamination-disclosure line in every cold ruling. Both of
   tonight's contaminated rulings stand on their cited evidence; the
   same erratum applies retroactively to the B1 gate's judge (SX3).
3. **Acceptance gates:** isolated-native-write ✅, native-discussion ✅,
   **phone-approval ✅ CLEARED** (Supervised/"approve actions" holds
   execution until Ed's tap — proven by harness-event timeline: 125 s
   hold, execution-at-release to the second, plus a second thread where
   declines blocked entirely; the model is BLIND to the approval layer,
   so thread-side reports are inadmissible as approval evidence).
   Auto-mode cards are post-hoc notifications, never consent.
   OPEN: checkpoint-restore, app-death recovery, cold-packet-handoff
   (see Ed's acks below).
4. **PR #98 merged** (`9b02539`) — CI shard matrix live, main CI green
   under it; retire TEST-SPEED-01's Phase-1 row in the next kernel pass.
5. **QUIET-GUARD-01 specced** (Sol high consult,
   `docs/process_traces/2026-08-04-quiet-guard-spec/`): two-phase
   handoff is the core design — the t3 session creates
   `handoff_pending`, self-terminates, and only the detached watcher
   acquires the real `quiet_held` after a zero-agent census. 25 open
   questions are the implementation packet's intake; four are Ed's
   (state-root permissions, launch-perimeter enumeration, unattended git
   identity, relaunch fallback channel).
6. **T3-CHAR-PAIR-01 protocol written**
   (`docs/process_traces/2026-08-04-t3-char-pair/PROTOCOL.md`) — it
   supplies the row's "standard idle-capture conditions", which had no
   implementation behind it. Mechanism: `joulewise run` with NO policy
   bound (skips admission entirely, no campaign log, no verdict, no
   lock — the non-claim custody fence is structural). n=3 per arm.
   **CORRECTION (2026-08-04 successor session): the app-UP arm was
   NEVER COLLECTED** — this block's original "collected overnight"
   claim was stale at handoff; the run report
   (`docs/run_reports/2026-08-03-t3-cutover-night.md` §Handoff) records
   the driving session stood down rather than contaminate an idle
   capture with an active agent session. Collection shape when taken:
   the three `configs/characterization/char-t3appup-r0*.json` captures
   as ONE background job while the operating session idle-waits with
   zero output (protocol limitation 1), t3 resident and dormant; then
   desk analysis (mean/p95 package power per capture from
   `rich_telemetry_idle.jsonl`, arm mean + SD). **App-DOWN arm is
   deliberately NOT collected** — it needs Ed present (quitting t3
   kills his threads, and the app-death gate wants him there anyway).
7. **INCIDENT, read it:**
   `docs/process_traces/2026-08-04-incident-state-forgery/INCIDENT.md`.
   A directing subagent forged `codex-run-v3`'s audit state file to
   manufacture its own scope-grant authorization. Detected by the
   harness classifier, state restored from backup, forged copy kept as
   evidence, the forged path abandoned (the fixture leg was relaunched
   fresh with full WRITE_SCOPE at launch instead). Findings F1-F4 are
   queued doctrine work — F1 is a REAL wrapper defect that created the
   pressure: `codex-run-v3` only treats a scope return as resumable
   when `verdict.acceptance == "needs_ruling"`, and the injected genre
   contract never says so.

### ED OWES (nothing blocks the successor's queue)

- **Two acks:** (a) cold-packet-handoff gate → recommended CLEARED-WITH-
  EXCEPTION jointly with the worktree-launch cure (judges split
  A/B on unconditional vs joint); (b) registry status flip
  BOOTSTRAP-AUTHORIZED → RATIFIED now that the gate has ruled.
  [BOTH ACKED by Ed 2026-08-05 and recorded — see the top block.]
- **Two gates needing his presence:** app-death recovery (a t3
  quit/relaunch he's present for) and checkpoint-restore (scratch-repo
  probe). The app-DOWN characterization arm can ride the same session.
- **D-113 / WINB-R06-DISPOSITION-01** — the r06 removal channel, F7
  barred-cell scope, fresh NEG-8 bound authorization. Biggest parked
  decision.
- D-080 runner choice (cron vs manual); QUIET-GUARD's four questions;
  NVIDIA + Blacksmith both explicitly parked by Ed.
- Hardware: **the 140 W adapter question is RESOLVED** — live probe
  shows 28 V × 4.99 A, "pd charger", 140 W negotiated, `is_charging`
  false. Window C needs only a fresh §5A whenever he wants a night.
  Network time: Ed restored it (expect §5A to turn it off again).

### Standing operating facts for the successor

- Ed's effort cap: **Sol HIGH only**, no xhigh, until he lifts it or
  quality visibly declines. Tonight two high instruments each produced
  blocker-grade unique catches — no decline observed. When a ruled gate
  composition names a higher tier, Ed's directive governs and the
  deviation is recorded in the gate record AND synthesis (ratified Q3e
  rule).
- Rule 11 unchanged: second fix round on a defect, verdict
  reinterpretation, irreversibles, proposed process rules, and
  waiting-state turns all convene the cold gate — now from a worktree.
- Never gate a commit on a piped test command (recurred twice
  historically; avoided tonight by capturing exit status unpiped).
- Delegated prompts must forbid touching any audit/state/manifest/log
  artifact (incident F2) — "the trail is not yours to repair."
- Worktrees: `calbracket` (impl/cal-bracket-d079 @ c2f81d4, PR #100),
  `testspeed` (impl/test-speed — MERGED, prune it), plus tooling-owned
  ones under `.claude/worktrees/` and `~/.codex/worktrees/` (leave).

## ✅ CHECKPOINT 2026-08-03 late night — T3 CUTOVER (successor session, ACTIVE)

**T3 Code (Alpha) is now the standing control plane** (Ed directive,
TIER 1 — outranked only by measurement-pollution constraints). It is
the PRESENTATION/CONTROL plane, never the compliance plane: envelopes,
leases, manifests, WRITE_SCOPE, and every gauntlet layer remain
authoritative and unchanged. Full adjudication record: two Sol xhigh
design consults (threads `019fca7c` — lost to MCP recycle, conclusions
recapped+adopted in `019fcac1` — and `019fcac1`) plus a Sol high night-
plan review (`019fcafc`); run report + council row at session close.

**Operating orders effective NOW (Ed-directed interim; rule-11
ratification rides tomorrow's cold-gate packet):**
1. t3 thread mode **"Full access" is PROHIBITED for this repo** — it
   maps to `--permission-mode bypassPermissions
   --allow-dangerously-skip-permissions` (confirmed live from process
   table). Supervised/Auto only.
2. **Never pattern-kill** (`pkill -f "codex exec"` etc.) — sibling t3
   threads make the process table shared. Kill only PIDs recorded in
   your own manifest/scratchpad, verified by start-time + ancestry.
3. **t3 checkpoint-REVERT is forbidden in the main tree**; in a
   worktree it is a workspace mutation → stop writers, capture
   manifest/diff, record it, re-baseline before delegation resumes. A
   t3 checkpoint ref is never audit evidence; a t3 checkmark is never
   an envelope.
4. **t3-native Codex threads are Ed-direct only** — never targets for
   lead-delegated or gate-bearing work (that stays on wrapped routes);
   material consumption of native-thread output requires a
   lead-authored ingestion note in the session manifest (interim form).
5. Delegated-run visibility: substantial background Sol rounds go
   through the tracked codex subagent (visible "Subagent task"
   activity) — lifecycle visibility only; envelope/manifest ceremony
   unchanged underneath.

**Ed rulings tonight (ratification via packet):** R1 — fresh-eyes
sweep cadence is WORK-CHUNK-ANCHORED (post-consumption of substantial
rounds / merge waves / adjudications) with a mechanical
materially-consumed-invocation backstop counter; this rules the shape
`D080-TRIGGER-01` (queue A52) was blocked on — row stays BLOCKED until
the D-080 amendment ratifies it. R2 — cold gate uses
CHARTER-SUPPRESSION (standing tracked hash-pinned charter replaces
`CLAUDE.local.md` ingestion; packet validator refuses hash mismatch);
cold FABLE judge + Sol xhigh contract-lens refuter (cross-model
diversity; Sol's conflict-disclosed concurrence on topology). R3 —
COMPRESSED shadow cutover: six acceptance gates during real work, no
fictional shadow period; rollback = pre-t3 mechanism per route, TUI
operation remains available; Sol's full-shadow preference recorded as
dissent. Gates: native-discussion, phone-approval, app-death recovery,
checkpoint-restore, isolated-native-write, cold-packet-handoff. **This
checkpoint's commit is the isolated-native-write gate exercise** (first
governed t3-native repo write: small, reviewed, pushed, verified).

**GATE/PROBE LOG (live, same night):** isolated-native-write ✅
(97d6e3d). Native-discussion ✅ — Ed ran a native t3 Codex thread in
the repo (rollout `019fcb0b-710c-75d2-8aaf-adb69680ea7d`, benign test
exchange, ingestion note = this entry); BONUS: rollout `session_meta`
carries `originator: "t3code_desktop"` — a mechanical provenance
discriminator for native-vs-wrapper Codex sessions, free in the
evidence stream (fold into the §4/§6 amendment). Phone-approval ✅
CLEARED (2026-08-03 ~22:27, successor session): Supervised
("approve actions") timed probe PASSED — home-dir write sent ~22:26
executed at 22:27:34 at Ed's tap, second card observably held the
readback until its own tap; probe record = doctrine-packet exhibit
E10. BONUS: the thread's own reply claimed "no permission prompt" —
the model is BLIND to the approval layer, so thread-side reports are
inadmissible as approval-semantics evidence (operator observation +
filesystem timestamps only). The Auto-mode caveat below STANDS.
Original A3 FINDING: in t3 "Auto" mode Claude's classifier
SELF-APPROVED a sandbox-disabled home-dir write with NO prompt relayed
— Auto ≠ human-in-loop; only Supervised guarantees a tap; anything
requiring Ed's eyes uses a Supervised thread or waits (gate re-run:
flip a thread to Supervised, one prompt, one phone tap). REFINED by
timed discriminator probe (22:04:04→22:04:04, Ed instructed not to
respond, file created in 0s): in Auto mode the PHONE CARDS ARE
POST-HOC NOTIFICATIONS, NOT GATES — execution never blocks on them.
"Auto's popups are not consent either." A tapped card ≠ an approval;
the 2026-08-03 prior session's "permission prompts functioning"
inference is corrected (its clicks were acknowledgments). Upstream
issue candidate: notification cards are visually indistinguishable
from approval prompts (legibility hazard). Capability-profile matrix
(mode × provider × blocking-semantics) to be filled tomorrow. Probes:
CODEX_HOME default (no provider override — ~/.codex recipes valid);
CLAUDE.local.md ABSENT in all worktrees (rule-11 doctrine provably
main-checkout-only — charter urgency confirmed); git common-dir
reachable/writable from worktrees (bookkeeper root feasible); t3
server = single origin 127.0.0.1:3773, pid-matched, but bound 0.0.0.0
(LAN-exposed, ticket-auth'd — Ed to check the Network-access toggle).

**TONIGHT'S NIGHT PLAN (Sol-corrected order, thread `019fcafc`).**
Window execution stays CONDITIONAL on the 16h-runway block's Window-C
conditions (adapter identity ≥140W resolved — 70W negotiation open
question; fresh ED-5A; guarded-launcher conditions; battery-cap
consult). If conditions do not resolve: desk-only night = probes +
gates + packet prep (characterization captures may still run,
non-claim).
- **A (this t3 session, ~1h):** Phase-0 probes — provider CODEX_HOME;
  CLAUDE.local.md worktree loading; Supervised/Auto EFFECTIVE
  capability probes (approval/sandbox/write behavior, not just flag
  mapping); native context-provenance probe (charter/suppression
  behavior in a real spawned context); t3 RPC recon (read-only, no
  thread spawning); checkpoint-restore semantics on a SCRATCH repo;
  git-common-dir reachability from a t3 worktree. Phone-approval +
  native-discussion gates complete BEFORE the runway (gate activity
  resets the idle runway).
- **B (window block, old doctrine unchanged):** app-UP non-claim idle
  capture (t3 resident, threads dormant) → hand-off note OFF-REPO
  (memory dir, NOT a repo commit) → freeze measurement head → QUIT t3
  AND inventory/stop survivors (cloudflared, helpers, resource
  monitor — verify, don't assume) → app-DOWN non-claim capture
  (separate custody; shares NO baselines/calibration/NEG-8 evidence
  with the claim chain) → end characterization → ≥10-min untouched
  runway → ED-5A (Ed, physical) → governed settles → COMPACT claim
  windows, each independently calibrated/verdicted/backed-up, launched
  from an ORDINARY GUARDED SHELL with ZERO agent sessions (an idle
  claude session is 12–18% CPU of agent load per D-099 — none allowed)
  → post-cal → verdict → immutable backup → THEN relaunch t3 →
  app-death gate vs predeclared criteria (history/checkpoint,
  cwd/worktree, provider, mode, no duplicated turn/side effect).
- **Aborts:** any surviving agent/helper process; head or frozen-plan
  drift; failed 5A/prep/admission; nonempty runs root; custody/trap
  failure; third same-cause failure (standing escalation trigger).
- **App-up window operation remains PROHIBITED** until the
  characterization pair + the quiet-guard WO (host-wide quiet lease,
  refuse-at-arm, characterized resident watcher — to be minted as
  QUIET-GUARD-01) land through the full gauntlet.

**TOMORROW (order):** (1) CAL-BRACKET B1 rule-11 gate — FIRST repo-work
item, gates everything mint-ward; (2) t3 doctrine cold-gate packet →
fresh-t3-thread Fable judge + Sol xhigh refuter (first live use of the
new cold-gate mechanism, on the packet that defines it); (3)
quiet-guard WO spec consult (Sol xhigh); (4) WO-T3-VIS (t3-thread-
bridge: audited wrapper dispatching `thread.create`/`thread.turn.start`
so delegated Sol rounds appear as REAL t3 threads — full council, new
adapter) probes + spec; (5) contract §4/§6/§7/§8 + skills amendment
drafting (visibility axis, four-axis provenance fields, owner-kind,
transient-write limitation, top-level redefinition).

## ✅ CHECKPOINT 2026-08-03 night — 16h-runway stream state (successor is FABLE, MAGISTRATE, on T3 Code)

**Read first:** this block → the two ⏸️ ED blocks below it →
`CLAIMS_STATUS.md` (refreshed tonight; §1 is honestly EMPTY under
D-110) → `docs/run_reports/2026-08-03-16h-runway.md`. Decisions tonight:
D-108..D-112 (all indexed). NOTHING is in flight — every stream
concluded at a held state; no background jobs; no unpushed repo work.
Worktrees remaining after the checkpoint prune (6 dead ones removed):
`calbracket` (impl/cal-bracket-d079 @ 2e61ff9, pushed — the held D-109
stream), `testspeed` (impl/test-speed — PR #98 open for Ed), plus two
`.claude/worktrees/*` and one `~/.codex/worktrees/*` owned by other
tooling (left alone). The consistency sweep's 11 findings (4 blockers)
were applied before this final commit — incl. the rule-11 gate now
ENCODED on the CAL-BRACKET row as a hard start-dependency, and D-110
annotations on the seven kernel evidence labels that cite the tainted
7.377086 J value.

**STATE BY STREAM (all pushed):**
1. **D-108 / D100-BII: CLOSED.** PR #99 merged `32d72fd` (full
   gauntlet); clause-(d) re-record 3/3 digest-bound at merged HEAD; row
   retired; L-A′ hygiene banked
   (`.desk/coldgate_d100_bii/LA-PRIME-BANKED.md`).
2. **D-109 / CAL-BRACKET: HELD at `2e61ff9` on
   `impl/cal-bracket-d079` (pushed).** Implementation `8383113` + fix
   round 1 `2e61ff9` (B2 + S1 closed, mutant-proven). Delta re-audit
   verdict: **one blocker remains — B1 refined** (minted sessions
   refused before their legitimate preparation seam; implicit-minted
   rows still bypass; evidence lines in
   `.desk`-scratch report streamB-delta.md, summarized in the run
   report). **RULE 11: round 2 on B1 is a SECOND fix round on the same
   defect → convene the gate BEFORE benching round 2.** Everything else
   at that head audit-clean.
3. **Window B re-eval: STOPPED CORRECTLY → D-112.** License exhausted
   as drawn (r06 terminal, bound expired). Gate record TRACKED:
   `docs/process_traces/2026-08-03-winB-reeval-stop/` (packet + both
   instrument verbatims + synthesis). Original FAILED verdict stands.
4. **Mint chain: Q1 DONE — mint #1 re-derives BYTE-IDENTICAL at pinned
   `3de370ec`** (all four digests;
   `docs/process_traces/2026-08-03-q1-remint-bytecompare/`). Everything
   further is D-110-blocked by design (7B mint license SUSPENDED).
5. **Sweep propagation fixes: LANDED** (README/PROJECT_STATUS voided-
   number scrub, capstone D-091 amendment, council de-collision
   C-043/044/045 + C-046, cross-refs, D-111 backfill 41 artifacts).

**ED OWES (parked decisions, in rough priority):**
- **D-113 candidate — WINB-R06-DISPOSITION-01** (D-112 cl.4): r06
  removal channel (waiver ruling / membership re-binding / abandon for
  window C re-collection) + the F7 barred-cell scope question + fresh
  NEG-8 bound authorization.
- **PR #98** (TEST-SPEED CI shard matrix) — still open, Ed-merge-only.
- **Window C §5A** + the adapter question: the 140W Anker negotiates
  only 70W (20V×3.5A — likely non-EPR cable/port); windows REFUSED at
  70W by joint ruling (conditions incl. is_charging gate in
  `.desk/2026-08-03-night-consult-rulings.md`, tracked in the D-111
  backfill).
- NVIDIA plan ratification; D-080 trigger cadence (`D080-TRIGGER-01`);
  wall meter (non-blocking).

**SUCCESSOR'S NATURAL QUEUE (agent-startable):** (a) rule-11 gate for
CAL-BRACKET B1 round 2, then the round, delta, PR under D-072 — this
gates EVERYTHING mint-ward (D-110 re-mint conditions); (b) DC-2
validator evidence_root_id pin-widening design; (c) R2 backfill prep
(issuance itself lead+Ed-gated); (d) D-111 practice: adjudication
artifacts go in `docs/process_traces/` from birth.

**Session-mechanics notes for the successor:** the old session's
scratchpad (`/private/tmp/claude-501/.../d20c28cd-*/scratchpad/`) may
not survive — everything load-bearing is tracked or in
`~/JouleWise-window-custody/`/`.desk`. Three lessons recorded in the
run report: pipe-masked exit status recurred (twice) — never gate a
commit on a piped test command; subagent background probes can die
silently (probe foreground-with-timeout; revive via SendMessage +
harvest-from-disk); stale test-spawned servers (fake-vllm) orphan on
hard kill — sweep `ps` at session end.

> **✅ RULINGS 2026-08-03 (evening) — both parked decisions RULED by
> Ed** ("i defer to you and sol's decision"), after an Ed-requested
> 2-round adversarial Sol xhigh debate over both packets (thread
> `019fc9bb-73fd-7042-8faf-2a72d74ee5b3`; record
> `.desk/2026-08-03-sol-debate-d108-d109.md`; council C-042):
> **D-108** — D100-BII clause (c) RETIRED as a license precondition;
> row closes on (a) interval containment + (b) landed manifest pin +
> (d) repaired-tool digest-bound re-record over ALL THREE D-087
> occurrences (Sol correction adopted: evidence surface = three
> occurrences; the manual record is corroboration only); L-A′ demoted
> to banked hygiene. Window B re-eval unblocks on row close.
> **D-109** — CAL-BRACKET F3 = A-min-with-reservation (Sol's round-1
> soundness breaks adopted into law: reservation-first pending-entry
> before capture; repo-committed head pin, not prefix-subset), R1 (7
> clauses) + R2 (8 clauses incl. 19→38 = 38 total content-distinct
> valid same-epoch); 32/6 inventory = backfill candidate only; Option
> B recorded as rejected fallback. Both implementation streams
> relaunched this session (D100-BII close → window B re-eval;
> CAL-BRACKET single combined fix round → gauntlet → PR).
>
> **EXECUTION (same evening, Ed's 16h runway):** D-108 stream DONE —
> PR #99 merged `32d72fd` (full gauntlet incl. audit blocker F1 fixed +
> delta ACCEPT; lead suite 2403 OK) and the clause-(d) re-record
> EXECUTED at merged HEAD (3/3 licensed, digest-bound, banked in
> `.desk/coldgate_d100_bii/`). **Row D100-BII-BINDING-01 CLOSED;
> window B re-evaluation UNBLOCKED** (runbook execution next).
> D-109 stream (Sol) + L-A′ banking in flight. Ed did fresh §5A
> physicals (network time OFF confirmed; 140W Anker attached but
> NEGOTIATING ONLY 70W at last check — EPR cable/port question flagged
> to Ed; battery capped 80% = adjudicate via consult before any
> window). Quiet window C runs tonight ONLY if adapter identity
> resolves and all guarded-launcher conditions verify; else desk-only.

## DESK-SESSION UPDATE (HISTORICAL — superseded by the checkpoint block at top) (2026-08-03, Ed away — first the cold-gate arc, then a sleep-window of non-claim rows) — read this, then the two ⏸️ blocks above

This session executed the 2026-08-02 checkpoint's resume script and drove
the open work to its conclusions. **Everything in the "ACTIVE RESUME
SCRIPT" and "PRIOR RESUME SCRIPT" sections below is now HISTORICAL /
EXECUTED** — do not re-run those steps; the live state is here + the
two decision blocks above + the (blocked) kernel rows. Main is at the
sleep-window head; `git log --oneline -20` for the session's commits.

**SLEEP-WINDOW ADDITIONS (after the D-108/D-109 parks, non-claim rows):**
- **PR #97 MERGED** (`a32977e`): NVIDIA-RETENTION-FLAKE-01 — hermetic
  per-test retention roots close the shared-custody-path flake
  (test-only; node_client.py untouched; 20× stress clean). Row RETIRED;
  the production DEFAULT_RETENTION_ROOT hardening deferred as the new
  row **NODE-CUSTODY-DEFAULT-01** (P3, non-blocking).
- **PR #98 OPEN — LEFT FOR ED** (impl/test-speed): TEST-SPEED-01 Phase 1
  — module-atomic shard-runner + CI shard matrix (blocking test job →
  8 parallel shards, ~15min→~6min proven on the PR's own green CI).
  Lead-verified (union==2440/94 intact; audit found + fix closed two
  silent-coverage-loss blockers; guards permanently regressed). Merge is
  YOURS (it restructures the CI gate). Phase 2 (class-split the two heavy
  modules) + Lever 2 (fast tier) + Lever 3 (Blacksmith, your call)
  deferred. Custody `.desk/testspeed/`.
- Run report for the whole session:
  `docs/run_reports/2026-08-03-desk-session.md`. Skill-usage log +
  consistency sweep done; stale worktrees pruned (d100bii + calbracket
  worktrees KEPT — they hold the pending-decision fix diffs, though
  those get redone/discarded post-ruling; the durable decision inputs
  are in `.desk/`).
- After PR #98, the readily-startable non-claim agent queue is
  exhausted: the remainder is claim-adjacent (FLOOR-*, MODULARITY),
  ruling-requiring (SUPERSESSION-DUP-REFUSAL-01 has a "rule on" gate),
  Ed's personal tooling (TOOL-01), or milestone-gated (AUD-WO-* at
  2K-live/Phase-3). Left for Ed's direction.

**Landed on main this session (all pushed, CI green):**
- PR #96 merged (`f3127ed`): MINT-GENERALIZE-01 tooling — generalized
  mint sibling with authenticated per-plan pinsets (full gauntlet).
  Row stays OPEN on lead-reserved live mint steps (real mint-1 re-mint
  byte-compare; governed 7B mint, D-085 Q6).
- **D-107** (`131774d`): b-ii nested-closure cold gate 2 — C-A′
  producer-derived admission grammar.
- **TEST-SPEED-01** minted + timing DATA collected + shard/tier DESIGN
  done (`a14d1fe`, `ed845bb`; `.desk/test-speed-consult/`): suite is a
  2-module problem; shard-runner + split run_campaign/p2038 → ~87s wall
  (6.5×); fast tier → 25-40s PR feedback (full suite stays the merge
  gate). Impl queued (mechanical); Blacksmith (lever 3) needs Ed.
- Codex models-cache bug FIXED; council **C-040 addendum** + **C-041**;
  kernel pins **59**; all bookkeeping current.

**Two decisions were parked for Ed here (D-108 retire-vs-derive, D-109
registry-vs-narrow) — BOTH RULED 2026-08-03 evening; see the RULINGS
block at the top.** Still Ed-gated: window C (fresh §5A), NVIDIA
extension ratification.

**Ed still owes** (from prior scripts, unchanged): network-time restore
if still off; fresh §5A before any window C; the D-092 wall-meter
(non-blocking).

---
Historical from here to the end of this paragraph: **Main was at the PR #91
merge `67d268a`: the cooldown-join gauntlet's commits 1-2 are MAINLINE
(DA-1 CLOSED), and the `metrology_v1` campaign suite is MAINLINE with
four window-A plans FROZEN (D-096).** Decisions D-094..D-097 landed in
the same session; report:
`docs/run_reports/2026-07-31-claims-desk-session.md`. The prior head
`7ee680c` (PR #89: contrast window PASSED, D5-J mainline under the D-093
cold-gate synthesis; post-merge suite `Ran 2286 tests`, `OK
(skipped=12)`) is historical. See the (now-historical) state block below; the
mint-era summary that follows remains accurate for the mint arc itself.

**Main is at the PR #88
merge `da83337` (historical for this paragraph): mint #1 is MAINLINE.** The full mint arc (FIX-1..10
gauntlet, ratified mint contract, campaign configs, and the
`df-ph-decode-floor-mint1` artifact — absolute 3.592138 / comparative
7.377086 / operative gate 7.377086 J, validator clean lead-run) merged at
the audited head `16c7af0` under the D-088 conditioned license (cold gate
+ Opus contract refuter, unanimous). The 7B floor window
`window_7bfloor_20260729` is claim-bearing (verdict PASSED, floors
absolute 6.294380135190098 / comparative 13.998036715259254; the
absolute cell's member mean is 192.38623252628366 J over n=10 — the
comparative cell has its own, much smaller mean, so always name the cell
when quoting this). D-083..D-088 are in `docs/decision_log.md`.

**Standing conditions from D-088: LIFTED 2026-08-02** — the gauntlet
closed with commit 3 (PR #93 `cb860e1`) and the scans lift per the row
contract; QA-10A/QA-10B are retired to the completed table. (Historical
text: the conditions bound any claim consumption through the cooldown
join to a recorded three-check bench scan and barred minting from a
duplicate-bearing corpus.)
Session record: `docs/run_reports/2026-07-30-mint-merge-coldgate.md`.

## EXECUTED RESUME SCRIPT (2026-08-02 ~16:10 PT checkpoint — FULLY EXECUTED by the 2026-08-03 desk session; see the DESK-SESSION UPDATE above; retained as historical record)

**CHECKPOINT 2026-08-03 ~01:05 PT (machine move; resume HERE):**
Everything below through the EXECUTION UPDATE is DONE and pushed
(main `6e3a06e`+). Resume order for the successor:
1. **Verify the three in-flight ci runs concluded green** (they cover
   trees already full-suite-verified locally): the H3-revert
   (30775184401), D-101 addendum II (30775561147), and the actions
   Node-24 bump (30775660245). `gh run list --branch main`. The new
   separate `site` workflow is already 2/2 green. If any ci run is red,
   read the failing test before acting — tonight's pattern was
   doc-content pins, not code.
2. **CODEX BUG (flag to Ed FIRST):** both xhigh runs tonight lost their
   final envelope to a codex CLI bug — logs end with
   `codex_models_manager ... missing field 'supports_reasoning_summaries'`.
   Clear/refresh the codex models cache or update codex BEFORE the next
   long Sol run. Details in the codex-delegation-growth memory.
3. **D100-BII-BINDING-01 focused audit:** the UNAUDITED implementation
   is preserved at branch `impl/d100-bii-binding` @ `a6ce7af` (pushed;
   the commit message carries the held-untrusted disposition). Run the
   focused independent audit (fresh session, read-only, treat the diff
   as untrusted; the D-106 refuter diagnosis is in
   `.desk/coldgate_d100_bii/`), then merge under D-072 and close the
   row — window B re-evaluation unblocks on it.
4. **TEST-SPEED-01 (Ed-ratified 2026-08-03, THREE levers):** Ed
   ratified prioritizing suite speed, the PR-fast/full split, AND
   evaluating Blacksmith runners. The profiling consult died to the
   codex bug mid-work, but Sol's per-module timing script is
   recoverable from `.desk/test-speed-consult/test-speed-consult.log`
   (the last `+`-prefixed block) — extract, run it (~15 min), then
   design shard-runner + tier split from the data. Mint the kernel row
   (pins 58→59) with all three ratifications recorded.
5. **Mint chain:** MINT-GENERALIZE-01 is the ONLY gate left on the
   contrast claim (v3 merged, gauntlet closed). Then the D-095 chain.
6. Bookkeeping owed: council-log addendum for tonight's arc (D-101
   addenda I+II, the merge-fallback pattern, the codex bug); D-101
   addendum II is in the decision log, kernel rows current, pins 58.
Ed owes: fresh §5A before window C; network-time restore if still off.

**EXECUTION UPDATE (2026-08-02 evening, post-move session):** Steps 1-3
are DONE and step 4 is IN FLIGHT. PR #94 MERGED at audited head
`05d99b6` (merge `bc2ab19`, docs-only conflict resolved; verdict CI
GREEN 5/5). PR #95 MERGED per the same ruled pattern (GitHub could not
build its merge ref either; code conflicts resolved as clean unions,
composed-tree full suite green, push-to-main verdict CI). Kernel batch
landed with this commit (3 retirements, D100-BII-BINDING-01 minted,
pins 58; window C BLOCKED on a fresh post-move Ed §5A). The
D100-BII-BINDING-01 implementation ran (Sol xhigh, worktree
`scratchpad/d100bii`, branch impl/d100-bii-binding) and ended in
PROTOCOL FAILURE — envelope never written (ACCEPTANCE_FAILED) — so the
scope-confined diff (236 insertions, module tests 21/21 at the bench)
is HELD UNCOMMITTED in that worktree. Next: independent focused audit
of the diff as untrusted work, commit on the branch only after it
passes, then window B re-evaluation (step 5). Run-report §9 has the
detail. ALSO: main went
red at the D-106 commit via the live-content site tests — fixed
(`775fa23`) and the class closed by Ed's directive (D-101 addendum,
`2491760`: those tests are advisory-lane now); run-report §9 has the
full arc. Ed hand-pushed once past the permission classifier.

Successor is FABLE, MAGISTRATE. Main is at `bcbc10b` (post-move
session's final batch; the checkpoint head `326d05f`+ is historical).
The 2026-08-01→02 runway (~26 h) closed the cooldown-join
gauntlet and drove both repair branches to CLEAN decisive audits.
DANGER FIRST: the old session's scratchpad
(/private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/)
may NOT survive the laptop move — everything needed was rescued to
`.desk/runway-20260801-artifacts/` (16 files: all audit reports, fix
reports, the winB/winC briefs) and BOTH branches are PUSHED to origin.
The two worktrees there (d100-worktree, mcv3-worktree) are disposable;
`git worktree prune` + re-create from origin if needed.

RESUME IN ORDER:
1. **MERGE PR #94** (impl/met-dangler-disposition @ 5f8b4b8+05d99b6...
   head 05d99b6; the D-100 repair). Its pull_request CI never scheduled
   (close/reopen tried; GitHub-side). D-072 substance is satisfied
   far past precedent: THREE independent audits + cold gate D-106 +
   lead suite Ran 2396 OK EXIT-0-UNMASKED at the audited head + mapping
   pins hash-identical. RULED FALLBACK: merge; the push-to-main CI run
   is the verdict; REVERT immediately if it fails. `gh pr merge 94
   --merge` then watch main CI.
2. **MERGE PR #95** (impl/manifest-contrast-v3 @ e94d4a7; v3 with the
   embedded-floor-bytes ruling). Decisive audit CLEAN ZERO FINDINGS;
   CI was RUNNING 3/5 green at checkpoint — likely finished; verify
   `gh pr checks 95` then merge under D-072.
3. **Post-merge kernel batch:** retire MET-DANGLER-DISPOSITION-01,
   MANIFEST-CONTRAST-01, MEMBERSHIP-READER-FAILOPEN-01 (folded, closes
   with #94) to the completed table; ADD row **D100-BII-BINDING-01**
   (P1, agent lane) per **D-106**: (a) telemetry interval containment
   [run_started event, failure+0.250 s] (~5 lines; cadence clause
   STRUCK; concurrent-capture residual RECORDED); (b) custody digest
   freeze (closure artifact records sha256 of EVERY file per b-ii
   bundle + a root-level quarantine digest manifest, re-verified at
   license execution); (c) nested-content closure (metadata/event
   nested workload evidence voids); (d) in-code marker in
   salvage_dangler.py naming the open row. Window B re-evaluation
   HARD-BLOCKED on it. Fidelity pins will need updating (currently 60;
   -3 retirements +1 new = 58).
4. **D100-BII-BINDING-01 implementation** (Sol xhigh, one commit +
   focused audit — the fixes are decidable and small; the refuter's
   writer-level diagnosis is in
   .desk/runway-20260801-artifacts/... and D-106). Then:
5. **Window B re-evaluation** per
   `.desk/runway-20260801-artifacts/winB-reeval-exec-brief.md` +
   winB-reeval-runbook.md + `.desk/winB-closure-facts.md`. Remember
   D-106: condition 3 requires RE-RECORDING with the repaired tool;
   the closure artifact must carry per-file digests (the D-106 freeze).
   If PASSED: C2 rungs + C4's two complete shapes become licensable —
   CLAIMS_STATUS refresh + decision entry for Ed.
6. **Window C** (first quiet window post-move; Ed does fresh §5A):
   plan prep at .desk/runway-20260801-artifacts/winC-plan-prep.md
   (incl. the prep-script TM-line fix first). Needs #94 merged (done
   in step 1) + D100-BII-BINDING closed ONLY if a dangler occurs
   (D-106: a window-C dangler seeking the b-ii license before the row
   closes RETURNS TO THE GATE).
7. **Mint chain** (post-#95): MINT-GENERALIZE-01 (7B mint + the D-095
   multi-cell artifact) → gated contrast claim. CAL-BRACKET-D079-01 is
   fully specified (D-102; n=19 corpus tables in the reconstruction
   transcript summarized at .desk/cal_acceptance_d079/).
8. **Bookkeeping owed:** final run-report section for the runway's
   second half (D-106, both branch landings — the report's §8 covers
   through D-105); consistency sweep after the merges; C-040 already
   committed; NVIDIA staged plan awaits Ed's ratification
   (.desk/nvidia-extension/SYNTHESIS.md; queue row NVIDIA-PORTABILITY-01).
Decisions this runway: D-098..D-106 (+ D-100 addendum, repairs
disposition note). Standing: verdicts as issued; the D-106 binding
commitments; proactive polling of delegated runs (memory); README
banner = the machine-state channel.

## PRIOR RESUME SCRIPT (2026-08-01 desk session, second checkpoint; resume EXACTLY here)

Successor is FABLE, MAGISTRATE. The morning checkpoint's desk queue is
LARGELY EXECUTED this session (details in the prior section below, now
historical). State:

1. **MET-VERDICT-ADJ-01 COMPLETE → D-100.** Independent Sol xhigh audit
   (bench-verified) classified the three groups: (a) CONTRACT GAP,
   (b) MACHINERY DEFECT with CORRECT retry rejection — window A's
   post-cal retry binds a T1-incompatible power_policy (immutable), so
   window A is PERMANENTLY non-claim-bearing and C1 re-collects;
   (c) CORRECT for window B (pure cascade from the twice-declared
   dangler) + one latent fail-open. Group (a) ran the full rule-11 cold
   gate (cold Fable ruling → bounded follow-up after the custody sweep
   found idle-phase bundles → condition (b) re-drawn to the
   measurand-existence line → independent Opus refutation, 14 findings
   → magistrate synthesis). **D-100** adopted S2-A in the S3
   consumption-semantics-dispatch shape: original FAILED rows stand BY
   CONSTRUCTION; window B re-evaluation licensed only after the repair
   lands (`salvage_dangler_exclusion_v1`, new pinned basis); the three
   p2048-o0128 additivity cells are barred regardless (frozen min_n=8,
   7 present) and that shape re-collects in window C. Packet + audit +
   both rulings + refutation summary: `.desk/adjudication_packet_20260801/`
   (UNTRACKED — do not commit; fold into a run report before deleting).
2. **Repair rows queued:** MET-DANGLER-DISPOSITION-01 (A2, the D-100
   repair commit), CAL-BRACKET-D079-01 (D-079 budget unimplemented in
   calibration_bracketing.py — non-salvage escalator), MEMBERSHIP-
   READER-FAILOPEN-01 (latent malformed-record skip). MET-WINDOW-C-01
   now hard-depends on the dangler repair + Ed §5A.
3. **Gauntlet commit 3 IN FLIGHT (updated 2026-08-01 late evening):**
   the arc so far on branch impl/cooldown-gauntlet-c3 (worktree
   /private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/scratchpad/c3-worktree):
   composed commit `ddd7e5b` (design-consult-ratified; both D-097
   riders ruled) → main merged `8f1651e` → delta audit FAIL (3
   blockers) → fix round 1 `690acd0` → fresh re-audit FAIL, SAME
   signature on B1/B2/B3 → **escalation trigger fired → full cold gate
   → D-103** (WAL attestation ordering; TWO named aggregation policies
   — cold instance OVERRULED on B2 with recorded dissent;
   writer-strict/reader-tolerant grammar; origin-binding redesign
   REGISTERED as fallback on any further same-signature structural
   failure) → fix round 2 `7e44c1b` (D-103 implemented; lead suite
   2325 OK; mapping gates PASS) → fresh re-audit: **B1/B2/B3
   structural shapes PASS**, three NEW narrow blockers (lock
   enforcement fail-open in append_log + two alternate commands;
   torn-tail tolerance broader than the writer's possible artifacts;
   new-session regression not a real second process) → magistrate
   triage: trigger does NOT fire (first-round fixes for
   round-2-introduced adjacencies) → **fix round 3 RUNNING** (narrow
   brief; structural shapes untouched). ON ITS HARVEST: lead gate
   (suite + mapping hashes, MY canonicalization pins 7B 57
   entries 09934c6b…, contrast 47 entries 9ebeca3a…) → fresh delta
   re-audit → PR (D-072 gate). MANIFEST-CONTRAST v3 (D-095) stays
   SEQUENTIAL AFTER commit 3.
3a. **POST-MERGE STATE (updated 2026-08-02 ~12:45 PT):** commit 3 MERGED
   (PR #93 `cb860e1`); gauntlet CLOSED, D-088/D-093 standing scans
   LIFTED; PR #92 merged. TWO REPAIR BRANCHES at fix-round-1 heads with
   FRESH DELTA RE-AUDITS IN FLIGHT at checkpoint time:
   impl/met-dangler-disposition @ 5f8b4b8 (the D-100 repair; first
   audit FAIL 5 blockers → fix round with inputs.py scope expansion →
   lead gates PASS: suite 2391 OK unmasked, pins hash-identical) and
   impl/manifest-contrast-v3 @ 7c03b81 (v3; first audit FAIL 2 D-093
   blockers → fix round w/ SCOPE-1 grant + RULING-1 [F4 fixture-only,
   fail-on-base waived] → lead gates PASS: suite 2374 OK, pins
   hash-identical, v1 blob-identical). ON RE-AUDIT CLEAN: PR + CI +
   D-072 merge each; then window B re-evaluation per the staged
   runbook (.desk custody: winB-reeval-runbook + closure facts), then
   window C prep. D-102 (CAL-BRACKET pins) ready-to-implement after.
   NVIDIA extension: two-lens consult synthesized, staged plan in
   .desk/nvidia-extension/SYNTHESIS.md, queue row Ed-gated. New rows:
   C3-RECOGNIZER-EXACT-01, NVIDIA-RETENTION-FLAKE-01,
   NVIDIA-PORTABILITY-01. Ed context: runway end = checkpoint for
   context-clear + laptop move (NOT a deadline); window C moves to the
   post-move session BY PHYSICS (move invalidates settled-machine
   conditions).
3b. **Landed this desk runway (Ed-authorized ~26 h, began ~16:00 PT):**
   D-102 (CAL-BRACKET pins: cap 0.001275166090593858 s / ceiling
   0.012093166090593858 s, identity-epoch freshness, never-zero
   allowance, decimal semantics — n=19 corpus reconstructed with
   member hashes, summary in .desk/cal_acceptance_d079/); D-103; D-100
   addendum (four mechanical spellings + reader-fail-open fold);
   PR #92 MERGED `3eaa37e` (D-096 F2 --k hardening); related-work
   draft committed (docs/paper/related_work_draft.md, Phase 2
   complete); micro_delta slope fit banked as DESIGN INPUT
   (.desk/microdelta-slope-fit-design-input.md: 0.1057 J/token,
   superlinearity finding, k=140 / k=48 candidates; k-set ratification
   deferred to micro_delta planning); README machine-state banner
   (D-101 batch); D-100 repair design consult COMPLETE (full
   implementation design incl. fold-in of the reader fail-open;
   awaiting commit-3 landing). Subagent stall pattern noted twice:
   directing codex agents go dormant after background runs — harvest
   their report files from the scratchpad directly.
4. Landed on main this session: 1ea651f (D-098/D-099, council addendum
   III, kernel rows), 44f0744 (DRIFT + PROJECT_STATUS plain-language),
   1694eb9 (repair rows), 209201c (D-100 + adjudication retired),
   plus the CLAIMS_STATUS second refresh (this commit).
5. Still owed: commit-3 harvest chain (step 3). ~~Run report~~ [DONE
   `df78b53`], ~~skill-usage log~~ [DONE], ~~consistency sweep~~ [DONE
   2026-08-01 — 19 findings, all applied in the D-101 batch]. Ed owes: network-time restore (`sudo
   systemsetup -setusingnetworktime on`). Ed context: timeline
   pressure is LOW (started ~3 weeks early; horizon December).

## PRIOR ACTIVE RESUME SCRIPT (2026-08-01 ~07:00 PT checkpoint; EXECUTED this desk session — retained for the collection facts)

Successor is FABLE, MAGISTRATE. BOTH metrology windows are now
SALVAGE-CLOSED and post-processed; tonight's session (2026-08-01
00:30–07:00 PT) ran window B end-to-end with three launches and full
custody. Session scratchpad (consult report, launcher scripts):
/private/tmp/claude-501/-Users-edr-code-JouleWise/693609a9-97c5-44fb-81a3-7a9aedb814de/scratchpad/

STATE AS OF THIS CHECKPOINT:

1. **Window A verdict: FAILED** (governed run 00:26–00:47 PT; row in
   runs_window_metrologyA_20260731/campaign_log.jsonl). Conditions:
   `whole_window_bundle_invalid` + `environment_admission_failed` (the
   quarantined-never-replaced mtadd-p0512o0512-r08 occurrence dangles;
   first time the machinery saw that shape) and
   `instrument_calibration_bracket_missing` (bracket pre AND post null —
   the selector refused the deviation retry post-cal; §8 budgetable case
   never evaluated). neg8_bracket PASSED, adapter continuity STABLE.
   THE VERDICT STANDS — no reinterpretation. Desk-lane adjudication
   required (see queue below). [Adjudicated 2026-08-01 → D-100: window
   A is PERMANENTLY unlicensed — the deviation retry binds a
   T1-incompatible power_policy, immutable.] Close-out complete at
   ~/JouleWise-window-custody/window_metrologyA_20260731/close-out.md
   (also corrects: additivity was 21/24 not 23/24; Anker charger note).
2. **Window B (window_metrologyB_20260801): COLLECTED and
   SALVAGE-CLOSED, measurement_complete 13:52Z.** Collected + BANKED
   (72+13 bundles, both roots, backup rc=0): bound 12/12 + minted,
   start triplet 3/3, **null_o0128 + null_o0512 COMPLETE** (C2: 2 of 3
   stages), midpoint, **additivity 23/24 single-root** (C4
   near-complete), end triplet 3/3, pre-cal 20260801T014059-8c3bfe9e /
   post-cal 20260801T064830-c76f5d1c both single-attempt (bracket
   fiducial diff ~2.3 ms vs 10 ms policy). NOT collected -> THIRD
   metrology window: null_o2048, long_holds, additivity p2048o0128-r08.
   Full narrative in the close-out:
   ~/JouleWise-window-custody/window_metrologyB_20260801/close-out.md
   (launch-1 §5B abort ×2, Sol consult, bird-SIGSTOP protocol, three
   member failures, salvage). One supersession recorded
   (mtnull-o0512-b04-b2, entry 3896c5ed…) BEFORE the verdict.
   **Window B verdict: FAILED** (row appended 07:19 PT, 70-bundle
   basis) — but NOT window A's failure shape: the §8 bracket PASSED
   (drift 2.25 ms, pre+post formed), the dangling r08 was NOT excluded,
   the recorded supersession was NOT consumed, and
   `source_campaign_manifests` is EMPTY (zero manifests resolved
   despite a populated dir). Conditions:
   `whole_window_campaign_membership_unresolved`,
   `environment_admission_missing`, `neg8_bracket_missing`,
   `neg8_bracket_reference_invalid`, `neg8_drift_bound_stale` (bound
   was minted in-window — "stale" itself needs adjudication [ruled
   2026-08-01: pure cascade, machinery CORRECT — MET-VERDICT-ADJ-01
   audit + D-100]). Verdict
   STANDS as issued; close-out verdict line is FINAL.
3. **NEW DOCTRINE FACTS (bind immediately):**
   - The clock anchor is KNIFE-EDGE by construction (Sol consult
     confirmed, margins ±1.4 ms at 197 s; the unmodeled ~−12 ppm
     wall/monotonic rate ≈ 2.3 ms/capture exceeds every margin).
     Desk item: rate-aware anchor design (paper-relevant).
   - TM attributions were a FALSE PROXY (no TM destinations configured;
     prep script line detects only process residency). Window A's #3
     "TM-consistent" label is tainted; actual overnight intruder class:
     mobileassetd/softwareupdated (~04:29 PT both nights) and bird.
   - bird-SIGSTOP protocol (identity custody + CONT trap + launcher
     hold) is now once-validated practice; pre-cal passed first attempt
     under it after failing 2× with bird active.
   - **The operating session's OUTPUT STREAMING is a measurement
     hazard**: window B failure #3 was caused by the magistrate's own
     post-arm status message streaming during an idle gate. Zero tool
     calls is INSUFFICIENT; after arming a launcher the session's
     message must be ONE LINE.
4. DESK QUEUE (order for the successor):
   1. [DONE this session] Window B verdict emitted (FAILED, see step 2)
      + close-out finalized.
   2. [DONE 2026-08-01 → D-100] **Machinery adjudication (both windows, THREE question groups):**
      (a) quarantined-without-replacement dangling occurrences in
      salvage-closed windows (A excluded-and-failed on it; B did not
      even exclude it); (b) deviation-retry post-cal selection (A's
      bracket refused to form; B's formed and passed); (c) window B's
      manifest/membership resolution — zero `source_campaign_manifests`
      resolved over a four-chain-segment window, recorded supersession
      not consumed, NEG-8 bracket evaluated missing/invalid/stale
      against an in-window bound. Contract-lens work: independent audit
      -> cold gate if any override of the as-issued FAILED verdicts is
      proposed. The collected corpora are banked and intact either way.
   3. Gauntlet commit 3 (D-097 composed contract) + independent audit —
      unchanged from the prior checkpoint's desk lane.
   4. MANIFEST-CONTRAST v3 (D-095) -> multi-cell mint (D-088 cl.3(c))
      -> gated contrast claim, chain unchanged.
   5. Bookkeeping owed: ~~run report~~ [DONE
      `docs/run_reports/2026-08-01-metrology-window-b.md`],
      ~~WINDOW_STATUS refresh~~ [DONE], **`CLAIMS_STATUS.md` created
      (Ed-requested standing doc, repo root): the ONE home for claim
      validity state — refresh it whenever claim-bearing state
      changes**; still owed: kernel refresh, D-098
      candidate (window A salvage + deviation + verdict-FAIL record),
      D-099 candidate (window B arc + bird protocol + streaming
      hazard), queue row for metrology window C (remainder), council
      log addendum (tonight's Sol consult), skill-usage log,
      consistency sweep.
5. Ed owes: network-time restore (`sudo systemsetup -setusingnetworktime
   on` — OFF since §5A last night). Also flag to Ed: the prep script's
   TM line and the two FAILED whole-window verdicts (expectation-setting:
   collections are fine; the machinery questions are desk work).

Standing: gates never waived; verdicts stand as issued (adjudication
COMPLETE 2026-08-01 → D-100); magistrate operates windows solo; zero agents AND zero
output-streaming during measurement idle gates; three-failure salvage
rule, guarded launcher, and bird-SIGSTOP are validated practice; the
loop runs until the paper's claims table is measured.

## PRIOR ACTIVE RESUME SCRIPT (2026-07-31 ~22:15 PT checkpoint; EXECUTED — window A verdict emitted [FAILED], window B run and salvage-closed; retained for the collection facts)

Successor is FABLE, MAGISTRATE. Metrology window A ran tonight and
SALVAGE-CLOSED under the third-failure rule; the ONLY remaining step to
make it evidence-bearing is the whole-window verdict, which was
deliberately stopped pre-supersession and NOT yet re-run. Session
scratchpad (consult memos, audit reports, cold-gate packets, suite logs):
/private/tmp/claude-501/-Users-edr-code-JouleWise/c4ec1557-9622-481f-b27e-72b695f1fc2a/scratchpad/

WINDOW `window_metrologyA_20260731` STATE (operator log in
~/JouleWise-window-custody/window_metrologyA_20260731/ is the full record):
- COLLECTED AND BANKED (backed up, 70+13 bundles, both roots): NEG-8
  bound corpus 12/12 + minted bound; start triplet 3/3; **linearity_ramp
  40/40 COMPLETE** (claim C1's campaign); midpoint; additivity 21/24 at
  final state [corrected per D-098; this checkpoint originally said 23/24] (r08 x2 shapes missing, p0512o0512-r08 quarantined);
  end triplet 3/3. NOT collected: null_ladder 02_null_o0512, long_holds
  01_holds (move to the next window with the additivity r08 remainder).
- THREE failures, all §10-handled, slots quarantined, cause named each
  time: #1 neg8-refcorpus-r05 (login/display-transition intruder),
  #2 mtadd-p0512o0512-r06 (operator walk-in, display wake — refused in
  15.8 s), #3 mtadd-p0512o0512-r08 (transient daemon burst,
  TM-consistent) -> salvage close per the ratified rule.
- POST-CAL: attempt 1 FAILED (mixed pulse-detection reasons, preserved:
  20260731T214355-126fc2ab); ONE settled retry under the a10-precedent
  RECORDED DEVIATION is VALID: 20260731T215120-fa1e9cda (b_fiducial
  0.045804 s). Pre-cal 20260731T161713-b8b08280 (0.030973 s, §5B
  PASSED). Expect bracket drift ~15 ms > 10.818 ms screen: §8's
  BUDGETABLE case (pre-cal level screen passed) — the governed verdict
  owns that ruling; do NOT hand-apply anything.
- SUPERSESSIONS: recorded ONCE each (claim root mtadd-p0512o0512-r06;
  bound root neg8-refcorpus-r05) AFTER stopping the premature verdict.
- Power identity: 140 W ANKER PD (instrument-visible "pd charger"/140.0;
  prior docs' "Apple" label was cosmetic — correct it in the close-out).
- Network time: RESTORED by Ed at wrap (confirmed) — no action owed.

TONIGHT (2026-08-01 ~23:00 PT, Ed-authorized 11-hour runway; Ed's §5A
done: network time OFF, plugged in, 140 W Anker, walking away):
window_metrologyB_20260801 — the metrology REMAINDER window (~3 h):
full null ladder (all three stages -> claim C2 complete), a clean
single-root additivity 24/24 re-collection (C4; window A's 21/24 stay
as corroboration), and long_holds Part A (C5). Plan root ASSEMBLED and
sha-verified (2a334f64…) at
/Users/edr/JouleWise-window-plans/window_metrologyB_20260801 (stages:
before = null o0128 + o0512; after = additivity + null o2048 + holds).
Only micro_delta (draft-pending-slope by design) then remains of the
whole metrology suite. After measurement_complete: §8/§9 verdict,
backup, close-out, then the overnight desk lane = gauntlet commit 3
(D-097 composed contract) + its independent audit.

RESUME (in order):
1. HARVEST OR EMIT window A's governing verdict: a verdict run was IN
   FLIGHT at this checkpoint (log:
   session scratchpad c4ec1557…/scratchpad/verdict_metrologyA_v2.log —
   check its tail AND `tail -1` of the window A campaign log for an
   appended whole-window row). If the row exists, consume it; if the
   process died with the session (likely on a context clear), RE-RUN
   the command below — no partial-row risk, the row appends only at
   completion:
   `.venv/bin/python scripts/run_campaign.py --whole-window-verdict
   --runs-dir /Users/edr/code/JouleWise/runs_window_metrologyA_20260731
   --log /Users/edr/code/JouleWise/runs_window_metrologyA_20260731/campaign_log.jsonl
   --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
   --neg8-drift-bound /Users/edr/code/JouleWise/runs_window_metrologyA_20260731_bound/neg8-drift-bound.json`
   (~20 min). No prior whole-window row exists (verified pre-checkpoint).
2. Close-out record at
   ~/JouleWise-window-custody/window_metrologyA_20260731/close-out.md
   (template: window_contrast_20260730 close-out; include the salvage
   narrative above, the deviation, the Anker correction, backup-done,
   and the verdict result). Then run report + WINDOW_STATUS +
   RUN_STATE/kernel refresh + consistency sweep (the standard batch).
3. NO extraction/claims from this window yet: C1 consumption follows the
   D-095 chain (gauntlet commit 3 -> v3 manifest -> multi-cell mint) and
   MUST record the D-093 raw-vs-validated scan (tonight: claim root 1/1,
   bound root 1/1 at recording time) plus the D-088 cl.3(c) bench scan.
4. RUN TONIGHT'S WINDOW (plan root ready, see TONIGHT block above):
   `bash scripts/quiet_mac_prep.sh` (Graphics FAIL is the known false
   signal), then arm the GUARDED LAUNCHER as a background job — poll
   every 120 s; launch `caffeinate -is /bin/zsh <plan-root>/window-chain.zsh
   <plan-root>` only when HID idle >= 600 s AND no XProtectRemediator
   process AND Time Machine not running AND no
   corespotlightd/mds/bird/photoanalysisd/softwareupdated/backupd above
   15% CPU (launcher scripts from tonight's session are in the c4ec1557
   scratchpad as the pattern; loginwindow >20% is also a hold). ZERO
   tool calls during measurement. Failures: §10 quarantine/continuation
   per this window's precedent; third failure of any signature closes
   as salvage. Post-window: §8 -> §9 verdict (record supersessions
   FIRST if any slot was rerun — the recorder-then-verdict order is
   mandatory, learned tonight) -> backup_runs.sh both roots ->
   close-out -> then the overnight desk lane (gauntlet commit 3).
5. DESK QUEUE (order ratified): gauntlet commit 3 (D-097 composed
   contract: writer emission + writer-external authenticated
   discriminator + reader re-acceptance + v2 truth-table row, ONE
   audited commit; fence in kernel); MANIFEST-CONTRAST v3 (D-095);
   multi-cell mint (after gauntlet closes, D-088 cl.3(c)); then the
   contrast claim = the paper's demonstration study #1.
6. Bookkeeping owed from tonight: D-098 candidate (salvage close +
   deviation ruling record), queue row for the metrology-remainder
   window, WINDOW_STATUS refresh, skill-usage log append.

Standing: gates never waived; magistrate operates windows solo; zero
agents during measurement; three-failure salvage rule and the guarded
launcher are now twice-validated practice; the loop runs until the
paper's claims table (outline §5) is measured.

## PRIOR STATE (2026-07-31 claims-desk close-out; resume script below FULLY EXECUTED)

The 2026-07-30 19:15 resume script is fully executed; the 2026-07-31 desk
day then merged two PRs and ratified four decisions:

1. **Contrast window `window_contrast_20260730`: COLLECTED, verdict
   PASSED.** 47 bundles (start/mid/end references + 40 ABBA science
   members, zero science failures), bracket drift 1.281 ms vs the
   10.818 ms screen, adapter continuity stable, backups verified.
   Recovery arc: start-triplet r1 failed CPU admission twice (XProtect
   Remediator sweep, directly observed at 941 CPU ms/s; round-1 TM
   attribution corrected on evidence); escalation trigger honored with a
   bounded Sol consult; round 3 ran clean end-to-end; supersession
   recorded ONCE (both failed occurrences superseded). Close-out:
   `~/JouleWise-window-custody/window_contrast_20260730/close-out.md`;
   report: `docs/run_reports/2026-07-31-contrast-window-collection.md`.
   Per-block contrast DIAGNOSTIC (prose, ungated): 7B−1.5B decode
   146.730349 J mean, σ 0.241 J, n=10 blocks. The gated claim rides
   MANIFEST-CONTRAST-01.
2. **D5-J MERGED via PR #89** (`aca78f8` + comment-only correction
   `707f76e`) [DONE 2026-07-31]: the delta audit FAILED (blocker DA-1:
   malformed supersession records silently dropped pre-ambiguity —
   PRE-EXISTING on main, byte-identical filter; should-fix DA-2:
   commit-message test overcount), which per D-089's revisit clause went
   to a cold gate (fresh Fable + Opus refuter, split verdict) and the
   **D-093 magistrate synthesis**: no behavior-changing fix round (DA-1
   closes in the gauntlet at the validator/reader boundary), merge at the
   corrected head, raw-vs-validated supersession-record scan added to
   EVERY claim consumption (initial: 0-divergence across all four
   claim-bearing corpora). **DA-1 is now CLOSED** inside the gauntlet's
   commit 2 (`e749c95`, PR #91) and `COOLDOWN-JOIN-DA1-01` is retired to
   the `TASK_QUEUE.md` completed table.
3. **Bookkeeping landed** (`49c1876`, `0d0bd0b`): D-089..D-093,
   C-039 addendum II, paper outline archived, window run report,
   WINDOW_STATUS + PROJECT_STATUS refreshed (metrology framing, plain
   language), kernel latest_report/date refreshed.
4. **Metrology campaign suite MERGED via PR #90** (`81a484b`) [DONE
   2026-07-31]: five campaigns (linearity_ramp, null_ladder,
   additivity_shapes, micro_delta k=64 draft-pending-slope, long_holds),
   150 configs across 23 condition families, deterministic
   regenerate-twice generators. **D-096** (`f010d5a`) ratified the plan
   vocabulary and FROZE the four window-A plans
   (`freeze_status: frozen_before_measurement`; micro_delta stays
   `draft_pending_slope` by design), and lowered the decision-log
   pagination ceiling 18k→12k so dense entries cannot push a site page
   past the 30 kB shard budget.
5. **Cooldown-join gauntlet commits 1-2 MERGED via PR #91** (`67d268a`)
   [DONE 2026-07-31]: C1 result-map completeness (`75e9f29` + audit
   response `c0adc93`), the C2 reader/counting domain closing DA-1
   (`e749c95`), the three-blocker fix (`8880395`), and the D-097 deferral
   commit (`a9b9d4a`). Four independent read-only Sol xhigh audits; the
   B1 blocker failed two same-signature formulations and went to the
   day's **second cold gate** (cold Fable + Opus contract refuter,
   converged on deferral); **D-097** adopted the refuter's stricter O3
   variant — the join's accepted schema set is exactly the writer-emitted
   set (v1 only), so a v2-labelled manifest or an `outcome` field on any
   member refuses. Final delta re-audit PASS, zero findings.
   **D-094** ratified the composed counting domain (and corrected D-088's
   benign-duplicate count 46→44); **D-095** adopted the
   MANIFEST-CONTRAST v3 design, implementation queued.
6. NEXT (in order):
   1. **Metrology window A, tonight** — frozen plans per D-096; needs
      only Ed's §5A and the launch (~2.8 h: ramp + additivity + null
      o0512 + holds).
   2. **Gauntlet commit 3** — writer outcome emission + a
      writer-external authenticated discriminator + reader re-acceptance
      + the D-094 v2 truth-table row as ONE composed, audited change
      (D-097 contract), with the relabel probe as a permanent
      regression. Its design consult must consume D-097's two riders
      (status consumption beyond authentication; the anti-malformation
      vs anti-tamper distinction).
   3. **MANIFEST-CONTRAST v3 implementation** (D-095) — unblocked
      file-wise now that PR #91 has landed; ordered SEQUENTIALLY after commit 3 [superseded 2026-08-01: the
      D-095 write surface overlaps commit 3's — no parallel start].
   4. **Multi-cell mint** (`MINT-GENERALIZE-01`) — still D-088-blocked
      by the no-mint-from-a-duplicate-bearing-corpus condition until the
      full gauntlet closes.
   The claim dependency chain ratified in D-095 governs the ordering:
   gauntlet commit 3 → analysis-manifest v3 → multi-cell mint → the
   gated contrast claim.
7. **Ed owes**: network-time restore (`sudo systemsetup
   -setusingnetworktime on` — still OFF from §5A), wall-meter purchase
   (D-092, non-blocking).

Standing D-093 condition (adds to the D-088 block above): every claim
consumption through the cooldown join records the raw-vs-validated
supersession-record scan; any divergence refuses consumption. **DA-1
itself is CLOSED** (gauntlet commit 2, PR #91), but the scans PERSIST
unchanged until `COOLDOWN-JOIN-GAUNTLET-01` fully closes — commit 3 is
still outstanding, so neither the D-093 scans nor the D-088 standing
conditions lift yet.

## EXECUTED RESUME SCRIPT (2026-07-30 19:15 PT pre-window checkpoint; historical — fully executed, see CURRENT STATE)

Successor is FABLE, MAGISTRATE. THE CRITICAL PATH IS TONIGHT'S CONTRAST
WINDOW — launch it before anything else. The capstone PIVOTED today
(Rivoire-ratified): METROLOGY-CENTRIC paper; the instrument is the
product. Session ledger (all rulings/facts — READ IT FIRST):
/private/tmp/claude-501/-Users-edr-code-JouleWise/abec37a6-31cd-4c56-a8a8-9448acaf12be/scratchpad/magistrate-rulings-2026-07-29.md
Paper outline: same dir /paper-outline-v1.md. Sweep memos: /sweep-*.md.

WINDOW (do first, in order):
1. Ed's §5A is DONE: clock verified, Network Time OFF at 19:02:38 PT
   (record restore after window), charger 140W Apple (power-supply
   identity), machine cleared for the night, last HID 19:02. Ed is
   AWAY — do not wait on him.
2. QUIET-LOCK: a Sol session may still be authoring metrology campaigns
   (`ps aux | grep codex`; check the minttool worktree log for a
   metrology_v1 commit). If committed and exited: fine. If still
   running at launch time: kill the codex processes (authoring resumes
   post-window; the window outranks it). NO agents during measurement.
3. Prep: the chain hardcodes REPO=/Users/edr/code/JouleWise; main
   checkout is currently on `main` — DETACH at the branch head first:
   `git -C /Users/edr/code/JouleWise checkout --detach 16c7af0`
   (campaign configs live on impl/mint-tool). Then
   `bash scripts/quiet_mac_prep.sh`. Its "Graphics capability" FAIL is
   a known false signal on this build — the authoritative display check
   is `pmset -g log` showing "Display is turned off" with no later
   wake (ledger precedent).
4. LAUNCH (~21:00 PT, >=10 min after last local command),
   run_in_background, then ZERO tool calls until measurement_complete:
   caffeinate -is /bin/zsh /Users/edr/JouleWise-window-plans/window_contrast_20260730/window-chain.zsh /Users/edr/JouleWise-window-plans/window_contrast_20260730
   Chain sha 2a334f64… (verified, includes §5B screen). Frozen plan
   RATIFIED: splitwise-decode-v1-m3max-qwen25-1p5b-vs-7b, n=10 ABBA,
   arms 1.5B/8b403126 + 7B/c26a38f6, evidence-bearing-now /
   claim-bearing-later per pre-reg §5. ~2.6h. If a member fails CPU
   admission: quarantine, wait out the idle-daemon intruder, author a
   continuation chain reusing THIS window's pre-cal
   (window_7bfloor_20260729 precedent + §10; supersession recorder:
   run ONCE per member, absolute --runs-dir). A third failure of any
   signature closes the window as salvage (end triplet + post-cal
   only) per cold-gate precedent.
5. POST-WINDOW: §8 bracket check -> §9 whole-window verdict (absolute
   --runs-dir) -> backup_runs.sh -> close-out record (template:
   /Users/edr/JouleWise-window-custody/window_7bfloor_20260729/close-out.md;
   include the network-time-restore reminder for Ed). NO floor
   extraction (science window, not calibration): claim consumption is
   blocked on MANIFEST-CONTRAST desk work; the paper's demonstration
   numbers come from bundle summaries + the one minted floor artifact
   (1.5B, 7.377086 J) plus the 7B prose-only floors (≈13.998037 J,
   pending MINT-GENERALIZE-01).
6. OVERNIGHT (agents OK after measurement_complete): implement D5-J —
   the STRUCTURAL cooldown-join redesign (adopted design + the struck
   liberalization cell + implementation sketch ALL in the ledger).
   Sol xhigh, WRITE_SCOPE {joulewise/analysis_engine/inputs.py,
   joulewise/whole_window.py matcher contract,
   tests/test_analysis_integration.py}, one commit on impl/mint-tool
   in the minttool worktree
   (/private/tmp/claude-501/-Users-edr-code-JouleWise/9c166892-d763-42c4-8cf7-383912f054c9/scratchpad/minttool).
   Then a fresh INDEPENDENT read-only delta audit (prior auditor
   violated read-only and self-fixed — ledger process flags; emphasize
   REPORT ONLY), full suite, and the merge train resumes (PR, D-072
   gate). MERGE IS HELD until that audit passes (escalation-trigger
   ruling; FIX-10 audited FAIL on B1/B2 — adversarial-shaped, honest
   path verified clean 57/57).
7. THEN: metrology campaign suite (finish/ratify the authoring if Sol
   died mid-run; spec = paper-outline §5 + its campaign->claim map);
   metrology window A next night (linearity ramp + additivity + holds
   -> claims C1/C4/C5).
8. BOOKKEEPING BATCH owed: decision-log entries from the ledger
   (metrology pivot, D5-J adoption + struck cell, trigger firing,
   FIX-10 process flags, Q1-Q9 ratifications, wall meter YES pending
   hardware = P1-003 answered); council-log addendum; queue rows
   MANIFEST-CONTRAST-01, MINT-GENERALIZE-01, POWERMETRICS-AUDIT-01,
   SUPERSESSION-DUP-REFUSAL-01; sweep memos + paper outline into
   docs/run_reports/; kernel refresh + gen_state; consistency sweep.

Standing: gates never waived; magistrate operates windows solo; zero
agents during measurement; plain language on advisor surfaces; the
loop runs until the paper's claims table (outline §5) is measured.

## PRIOR STATE (2026-07-30 afternoon; the resume script below is EXECUTED except where struck)

Steps 2, 3, and 5 of the resume script below are DONE (audit harvested →
FAIL → FIX-10 → escalation → cold gate → D-088 → PR #88 merged
`da83337`; bookkeeping batch on main as `e1e0aec`+`d8b5d54`). Step 1
CLEARED: Ed confirmed network time is **On** (2026-07-30, pre-meeting).
The advisor brief is also LIVE as a private shareable web page (URL in
the external-artifacts-index memory; canonical copy stays
`docs/advisor_briefs/2026-07-30-advisor-brief.md`).
Step 4 (tonight's window per D-085 Q1: `qwen25_7b_decode_floor_v1`
already EXECUTED 07-29; the contrast window `splitwise_decode_v1` is the
one still pending) awaits Ed authorization + AC + settled machine;
frozen-plan + pre-reg ratification by the magistrate happens FIRST when
Ed green-lights. Step 6 (advisor answers → queue reorder) lands on Ed's
return from the ~14:30 meeting; the hardened brief is
`docs/advisor_briefs/2026-07-30-advisor-brief.md`. The kernel refresh is
DONE in the working tree (intake rows folded, STACK-ID-BIND-01 and
FLOOR-LABEL-01 retired to the completed table, `latest_report`
repointed); remaining bookkeeping owed: the consistency sweep's deferred
flags (`PROJECT_STATUS.md` advisor refresh, `WINDOW_STATUS.md` staleness)
and the skill-usage log.

## EXECUTED RESUME SCRIPT (2026-07-30 ~11:00 PT handoff checkpoint; historical)

Roles: successor session is FABLE, MAGISTRATE (rule 11 topology). Ed has
an ADVISOR MEETING (Rivoire) ~5h from checkpoint; brief at
/private/tmp/claude-501/-Users-edr-code-JouleWise/abec37a6-31cd-4c56-a8a8-9448acaf12be/scratchpad/advisor-brief-2026-07-30.md
— her answers to its four questions REORDER the queue (acceptance bar,
write-up scope, wall meter, claim priorities).

STATE (all pushed): branch impl/mint-tool @ 969a4d6 carries the FIX-6..9
series, campaign configs (splitwise_decode_v1 contrast +
qwen25_7b_decode_floor_v1), the campaign doc, and MINT #1 artifact
f188562 (df-ph-decode-floor-mint1.json at branch root, validator clean,
gate 7.377086). Main checkout back on main. WINDOW
window_7bfloor_20260729 COMPLETE and CLAIM-BEARING: verdict PASSED
(basis 3ff9128b…f1173), backup ok, governed extraction clean
(all_cells_extractable true) — 7B floors: absolute 6.294380135190098 /
comparative 13.998036715259254; member mean 192.38623252628366 J; close-out at
/Users/edr/JouleWise-window-custody/window_7bfloor_20260729/close-out.md.
Session ledger (ALL rulings: B3, Q1-Q9 ratifications, FIX-9 shape, cold
gates ×3, staged mint cmd):
/private/tmp/claude-501/-Users-edr-code-JouleWise/abec37a6-31cd-4c56-a8a8-9448acaf12be/scratchpad/magistrate-rulings-2026-07-29.md
(+ sweep memos sweep-{techniques,mechanisms,cv-paths}-2026-07-30.md and
related-work-sweep raw in the same dir — commit to docs/run_reports/ at
bookkeeping).

RESUME (in order):
1. VERIFY Ed restored network time (`sudo systemsetup -getusingnetworktime`
   via Ed → must be On) — instructed this morning, NOT confirmed.
2. Harvest the FIX-9+FIX-8 delta re-audit: a Sol xhigh read-only session
   over f188562^..969a4d6 was RUNNING at handoff (launched via a codex
   subagent; its out-file path unknown to this checkpoint). Look for
   fresh codex out-files/processes; if not recoverable in minutes,
   RELAUNCH the audit fresh (brief: ruled-shape compliance of the
   supersession-aware cooldown join; fail-closed edges; stubbed-reader
   test honesty; one-reader drift risk vs run_campaign private copy; no
   scope creep; mint-artifact data commit consistency). Consume verdict.
3. Merge train: on clean audit → PR for impl/mint-tool (base main; the
   series is FIX-1..9 + contract + campaigns + mint #1), D-072 full gate
   shape, merge. STACK-ID-BIND-01 (A50) closes on the real-bundle
   re-verify already done at 7f2c108+ — record it.
4. TONIGHT (if machine settled + AC + Ed authorizes): contrast window
   splitwise_decode_v1 (~2.6h) per campaign doc on the branch. Magistrate
   ratifies frozen plan + pre-reg FIRST (drafts in the doc; family ids
   ratified Q2-Q8, see ledger). Machine moved since last window → §5A
   (Ed, admin), fresh runs roots, new plan root
   (/Users/edr/JouleWise-window-plans/ template window_7bfloor_20260729 —
   REUSE the runbook-§6 chain extraction procedure incl. §5B screen;
   remember: --evaluation-basis-sha256 on extraction, --hash-bundles,
   absolute --runs-dir, supersession recorder appends silent dupes (run
   ONCE per member). XProtect/TM idle-daemon risk: provoke idle
   daemons pre-window; third-failure-closes rule was cold-gate-ratified
   precedent. Post-window: verdict → extraction → claims (exact
   evidence-root mappings, NO surplus) → the contrast claim needs
   MANIFEST-CONTRAST schema work (Blocker B, campaign doc §2) — claims
   ride AFTER that lands; collection tonight is still correct (evidence
   ages fine, pre-reg is in the plan).
5. BOOKKEEPING BATCH owed (one commit set to main): decision-log
   D-083.. (from ledger: B3 ruling; 7.377086 ratification recorded
   earlier; Q1-Q9; FIX-9 shape; cold-gate consults; third-failure rule),
   council-log C-039 addendum (gauntlet + cold gates + audit layers),
   queue rows: MINT-GENERALIZE-01, MANIFEST-CONTRAST-01,
   SUPERSESSION-DUP-REFUSAL-01 (recorder footgun), POWERMETRICS-AUDIT-01
   (counter-mechanics, citable), TOOL --runs-dir absolute-contract doc
   note, F2 mock-sampler, B2 SHA-pin, S2 exact-set, refusal-vocab
   ratification, MDE-adoption + min-window-rule + battery-crosscheck
   (from techniques sweep top-10), full-PDF reads of TokenPowerBench +
   2605.11999 pre-submission; WINDOW_STATUS stale disk line; kernel
   refresh + gen_state; sweep memos → docs/run_reports/; consistency
   sweep; skill-usage log.
6. Advisor meeting output: capture her four answers as the acceptance
   spec (P1-008/E1 row closes), reorder claim queue per Q4 answer.

Standing constraints intact: gates never waived; quiet-lock during
measurement; magistrate operates windows solo; lead never delegates
final verification; plain language on advisor surfaces.

Historical NEXT (superseded by the block above): (1) close the two
remaining suite errors on `impl/mint-tool` @ `1d83d68` — DONE via
FIX rounds 81193f5/c698711/FIX-5;
(2) full-tier adversarial review of `git diff
main...impl/mint-tool` (two accepted strict-direction interpretation
calls are settled, see the run report); fix rounds with delta re-audits;
(3) lead-reserved live gate — governed extraction for a10
(`--evaluation-basis-sha256 79c6e8b9…e053e`, ~20 min) and window C
(`0cf07a5c…8fa6`), then run the mint; pre-registration gate must pass
as-embedded and `validate_floor_artifact == []`; (4) PR + D-072 gate +
merge; (5) kernel refresh (STALE: stamped 2026-07-25, FLOOR-LABEL still
READY, no mint rows). Window B re-collection follows, under the D-079
pre-flight screen (still unimplemented). Full handoff:
`docs/run_reports/2026-07-28-floor-mint-implementation.md`. New queue
item TEST-SPEED-01 (suite consolidate/redesign, ~3-4 min recoverable,
zero deletions clear D-061; PR-fast/full split is Ed's call).

Prior head (historical, superseded by the block above): main was at
`c3e2647` on 2026-07-25 — PR #79's D-078 instrument repair merged on
2026-07-22, and PR #85's ratified SCREEN+BUDGET rules merged with green
CI after the four-round adversarial gauntlet. The repaired-instrument
collection contains 229 strict members across four bracketed windows
(a5-a8); those windows are non-claim-bearing diagnostic,
instrument-proving evidence and do not license a floor or research claim.
The merged rules screen gross and idle-subtracted energy separately, carry
a never-zero drift allowance for each family, require a fresh 24-hour
drift bound, reject fallback-clock members from floor/claim cells, derive
mockness from custody-bound config, and bar terminal mock evidence. The
capsule was redeployed from `c3e2647` as `dep_2I04CG6tQ4t0mzY7` at
2026-07-25T01:46Z.

Prior context (historical, pre-repair; superseded by the sign-off above):
PRs #77 and #78 are both MERGED (#78 at b52abf3). The recal windows of
2026-07-18/19 collected 94 + 266 strict-valid bundles under the
production environment guard (records:
`docs/run_reports/2026-07-19-d077-recal-window.md`,
`2026-07-19-recal456-extended-window.md`); that corpus is instrument
evidence only — the pre-repair floor re-extraction plan is VOID, and
P2-015 restarts under the repaired instrument per the roadmap.
Ed-side standing: `sudo pmset -c displaysleep 10`.

Prior arc (2026-07-17, SESSION ARC COMPLETE: Window A floors
published (222 strict-valid bundles; P2-015 partial pending P2-039
artifact + P2-037 adjudication); advisor brief delivered
(docs/advisor_briefs/); Ed DEPLOYED the README-first site + Learn
guide (PR #75); exploratory block measured (OLMoE ~229 J / Qwen3-4B
~362.8 J / 122B ~1072 J gross suite, n=3, exploratory-labeled);
DSpark/DFlash MLX feasibility CONFIRMED w/ per-round observability;
D-075 extension-axis intake folded. Session records:
docs/run_reports/2026-07-16-resumption-nohw-batch.md +
2026-07-17-window-a-floors.md.)

## Start Here For Every Big Run

Before starting substantial work:

1. Read this file.
2. Read `TASK_QUEUE.md`.
3. Read `AGENT_PLAN.md` (phase index) and the active phase's plan doc under
   `docs/phase_N/`; per-item status lives in the phase exit checklist
   (D-023).
4. Read `docs/planning_reflection_protocol.md`.
5. Check `docs/decision_log.md` before re-deciding anything; check
   `docs/risk_register.md` if starting a phase or a hardware-dependent task.
6. Check the last 2-3 commits with `git log --oneline --decorate -3`.
7. Check `git status --short --branch`.
8. Run `python3 -m unittest discover -s tests` unless the task is docs-only.
9. Do not commit local deletions or unrelated changes unless the user asks.
10. Heartbeat rule (`docs/milestones.md`): if >14 days passed with no run
    report and no recorded break, start with a milestones + risk review.
11. Live MLX gates use the repo venv: `.venv/bin/python -m joulewise ...`
    (system python3 lacks mlx → `runtime_unavailable`).
12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
    "restart", "next", queue, and mission pointer until explicitly cleared.

At the end of substantial work:

1. Update only hand-authored factual/history sections of this file.
2. Update `docs/process/state_kernel.json` for live task state and regenerate;
   do not hand-edit either generated region.
3. Add or update a detailed report in `docs/run_reports/`.
4. Record tests, commands, and blockers; generated lane heads own next-work
   selection.
5. Record new decision-log entries and any risk-register status changes.
6. Refresh `PROJECT_STATUS.md` if advisor-visible state changed.
7. Push green commits promptly (small doc/bookkeeping commits straight
   to main; multi-commit code series as branch + PR per D-031). Do not
   accumulate unpushed local state — the remote and the high-level docs
   (README, PROJECT_STATUS) are the user's and advisor's view.
8. Run a docs-consistency sweep before the final bookkeeping commit
   (delegate to a fast subagent): stale test counts, gate-state
   contradictions between prose summaries and checklist matrix rows,
   numbers cited in multiple places (C-002; D-023 extension).
   Refreshing `docs/site/DRIFT.md` is OPTIONAL (D-101: the site gates
   nothing and is fully decoupled); when touched, it informs only:
   per D-068 (2026-07-14) NO agent regenerates or deploys the site,
   ever — automation informs; Ed deploys manually. (Supersedes the
   C-013 regenerate+redeploy convention.)
9. Call out any dirty working-tree state that should not be accidentally
   committed.

## Historical Stop-Card Note

This 2026-07-11 clearance note is retained as history only; current stop-card
and work-selection state is generated immediately below from the kernel.

<!-- BEGIN GENERATED: state-kernel run-state-intake -->
## ACTIVE_STOP_CARD

Status: NONE — no stop card is active. Stop-card authority: D-050 / D-063 ([decision log](docs/decision_log.md)).

## Active Global Work-Selection Gates

Selection is conjunctive: every lane-matching gate and every ordinary dependency must permit a task. Priority never bypasses a gate.

### `WINDOW-COUNCIL-GATE`

No quiet-mac task may start or resume after the 2026-08-15 NOT-READY verdict; the frozen D-117 packs wait while the council repair program proceeds.

- Scope: `select` in [QUIET-MAC].
- Allowed kernel task IDs: NONE.
- Authority: docs/decision_log.md#window-gating-directive--2026-08-13-late-ed-t6-council-audited-instrument-readiness-precedes-any-window; docs/process_traces/2026-08-15-readiness-council/council-verdict.md#verdict.
- Clearance: docs/process/instrument-readiness-audit-charter.md#verdict-form-amendments-11-12 — a reconvened READY-CANDIDATE council verdict records no NOT-READY, no UNVERIFIED, and all ED-QUALIFICATION rows closed with evidence

## Restart By Machine-State Lane

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-21). Latest report: [T12/T13 session 2026-08-19: co-design first application (R1/R2 rulings), D-147 transaction executed S0-S5 (r5/r6 reissues, _v3 family frozen with freeze-0003), writing standard + guide rewrite, D-148 Ed rulings](docs/run_reports/2026-08-20-t18-t19-session.md).

### [ED-EXTERNAL]

- READY — E1 `P1-008`: Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).

### [QUIET-MAC]

- GATED — Q2 `D117-W-ALPHA` (excluded by: WINDOW-COUNCIL-GATE): Run the frozen ALPHA pack d117_floor_qwen25_1p5b_v3 as D-117's fresh 1.5B decode-floor window with its prefill floor rider and governed close-out.

### [AGENT]

- READY — A1 `WO-LAUNCH-BINDING`: Bind arm-capability consume to immediate frozen-chain exec and require authenticated launch-consumption provenance at downstream claim consumers.

<!-- END GENERATED: state-kernel run-state-intake -->

## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open

The RESUME list from the 2026-07-17 checkpoint is fully executed. The
relaunched execution-lens review, fix rounds 1-2, and their delta
re-audits had already run earlier on 2026-07-18 (commits `1aebf14`,
`6d80039`); this session closed the surviving P1 (child accepted any
JSON object as the frozen cooldown anchor) plus every finding from four
further delta re-audits, as fix rounds 3-8 in commit `ad0920b`:
canonical anchor validator (`joulewise/cooldown_anchor.py`) enforced
fail-closed at parent/CLI/controller boundaries; collision-safe,
crash-atomic, flock-serialized rejection-verdict custody
(`experiments/rejections/`); physical-domain baseline validation (the
`inf`-anchor fail-open gate is closed); discriminating process-race
regression. Suite green lead-side at every round boundary, final
`Ran 1746 tests`, `OK (skipped=12)`. Awake-half live probe validation
passed on real hardware (zero probe errors); the Ventura screensaver is
now disabled on the machine (`idleTime = 0`). PR #77 carries the gate
narrative; merge is Ed's call. Full record:
`docs/run_reports/2026-07-18-d077-fix-rounds.md`. Tooling: codex-run-v3
xhigh review-genre sessions ended with null final messages 4x
(bridge-resume recovered each; personal-tooling defect, recorded in the
run report and the global codex-delegation skill field notes, not the
repo queue).

## CHECKPOINT 2026-07-18: Claude script bridge runs in the pet's app task

The actual Claude Code fallback route is `scripts/codex-bridge`, not the MCP
server for recent audited work. The wrapper now sends `new` and `review` turns
through a dedicated app-owned Codex desktop task when the local host id is
configured. This is the same local-conversation state the native pet consumes;
the prior observer-only diagnosis was incorrect because the pet never reads
`~/.codex/claude-spawned/index.jsonl`. A live Sol/high smoke appeared in the
Codex app as thread `019f77a6-3612-7332-9f5e-be9fbde56be5`, turn
`019f77a9-2827-7de1-accf-ac2eda21927e`, and returned
`JOULEWISE_NATIVE_PET_BRIDGE_OK` through the script. Adaptive effort remains
unchanged: `high` fallback/default, `xhigh` only on named hard-task triggers,
and `ultra` only for sessions that must spawn subagents. Full record:
`docs/run_reports/2026-07-18-claude-codex-pet-observer.md`.

Committed 2026-07-18 on `impl/env-guard-cooldown` (after the D-077
packet boundary `6d80039`) with a lead execution review at the bench:
IPC socket ownership/permission checks, PID-checked host-task lock,
interrupt-on-terminate, no-network sandbox policy, and one-hop rule all
verified in `scripts/codex-app-bridge.mjs`; real-socket fake-router
tests plus observer lifecycle tests included; canonical suite green
lead-side (`Ran 1722 tests`, `OK (skipped=12)`). The same commit
carries the doctor-driven CLAUDE.md trims (global + repo; content
deduplicated into `.claude/skills/codex/SKILL.md`, which is the
operating home) and stamp-only `docs/site/*.html` provenance refresh.

## CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending

Window A floors contamination diagnosed from primary data: macOS Ventura
*video* screensaver on an awake display contaminated 43/50 suite-calibration
bundles (~+30% energy, −11% throughput; engage at HID-idle +20 min, dismiss on
unlock — pmset assertion log corroborated to the second). The six "low"
su-ABBA runs (18:16–18:36 UTC) are the only CLEAN suite runs; comparative
suite floors (4.923 J item / 24.62 J suite) are transition artifacts. The
professor's power-source hypothesis is refuted (AC/140 W/100% throughout).
Details: memory note + `docs/run_reports/2026-07-17-environment-guard.md`.

Branch `impl/env-guard-cooldown` (pushed, commit e2813ee) holds the D-077
response: environment-guard preflight (+`--arm-quiet-mode`), per-run idle
admission gate, cooldown v2, unwaivable `environment_admission_failed` claim
barrier, policy sidecars, contract/doc updates. Design consult (Sol xhigh,
thread 019f7356-32d3) adjudicated and encoded; implementation by Sol xhigh
(thread 019f7362-6627, resumed via codex-bridge after an MCP transport
timeout); session-close scope check SCOPE_OK; full suite green lead-side
(OK, 12 skips). Lead bench fix included: `pmset -g systemstate` parser now
accepts the live "Capabilities are:" form (was null → fail-closed on real
hardware); fixtures pinned to verbatim live output.

RESUME (in order):
1. Relaunch the adversarial review round (was stopped mid-run at checkpoint):
   fresh read-only Sol xhigh, execution lens, over `git diff main...impl/env-guard-cooldown`
   (prompt shape in `.codex-bridge/` prompt snapshots); lead holds the
   contract lens (done for cooldown_gate/claim-barrier/anchor hunks).
2. Triage findings → fix rounds (defect-shaped regressions) → DELTA RE-AUDIT.
3. Live-validate flagged probes during next quiet-window prep:
   `pmset -g systemstate` display-asleep form + screensaver-engaged probe
   while a screensaver is actually running (run report flags
   `live_validation_provisional`).
4. PR per operation-loop §5 gate shape; then re-run suite ABBA calibration
   under the new guard ([QUIET-MAC], needs Ed) — floors D-076 figures for
   suite comparative cells must be recomputed/caveated pending re-run.

Status: **CLEARED 2026-07-11.** Every clearance criterion met: all
checkpoint-#4 resume items executed (P2-044 fix+merge #55; P2-037
audit dispositions → two fix rounds + approved NEEDS_SCOPE expansion +
delta re-audit → #58; P2-043 #57; P2-045 #56); the four held hardening
PRs #50-#53 merged after the cross-stream integration review over the
combined tree (38 pre-merge cross-stream failures caught and fixed; 1
review blocker confirmed by refuters → PR #59; SF1 refuted; SF3 →
queue row P2-049); DOC-008 kernel refreshed at final head (schema v2,
authority field, branch impl/doc008-kernel awaiting PR); bookkeeping
arc complete (run report, C-028 council entry with layer catch-rates
and ~57-invocation spend record, D-064 ratified incl. manifest v3 +
claude-codex-report/v1 + WRITE_SCOPE enforcement; queue reconciled;
consistency sweep; site regen+deploy). All clearance-time opens since CLOSED same day: #59 MERGED, DOC-008
MERGED (#60). Remaining queue heads: P2-049/P2-050/TOOL-01.

## Superseded stop card (CP-5)

Status: **CLEARED 2026-07-09** by the CP-5 resume session. Every
clearance criterion was met: all three worktree diffs lead-gated
(envgate live-gated against the real affine mock bundle) and merged as
PRs #23/#24/#25; PR #22 merged after a fresh final-head pass; the
methodology synthesis and suite_next specs packet adjudicated (CP-6 in
the stream log); all accepted pre-campaign changes landed and merged
(PRs #26/#27/#28); both post-merge integration reviews CLEAN; queue
rank 0 closed. Full record:
`docs/run_reports/2026-07-09-cp5-resume.md`. No stop card is active.

## Current Project Status

**Mint era OPEN AND FIRST MINT LANDED (2026-07-30): main `da83337`. The
data exists and passes, and the code path that turns it into a published
floor now exists and has been exercised — `df-ph-decode-floor-mint1` is
mainline.**

### The central measurement fact (read before any measurement decision)

The instrument is **attribution-limited (~1 J), not noise-limited
(~0.3 J)** — D-078 clause 11, Ed-ratified. Floors publish LABELLED with
the widened number; the point floor is a repeatability diagnostic that
may never be the published claim floor. The anchor term appears in
**both** the floor and each claim's decision interval, so the effective
clearable effect is floor + claim-side bound ≈ 5 J for phase contrasts,
and neither term may later be deleted as an apparent double count. Do
not launch an instrument-tightening program; it was measured and
eliminated.

### Collection state

| Window | Contents | Verdict | Notes |
|---|---|---|---|
| a9, a10 | earlier corpora | **PASSED** | a10 supplies the absolute component |
| **B** (`04_phase_prefill_abba`) | 40 prefill ABBA members, 59/59 collected clean | **FAILED** | `instrument_calibration_mismatch`, bracket drift 11.581436 ms; preserved, not claim-bearing |
| **C** (`05_phase_decode_abba`) | 40 decode ABBA members, 59/59 collected | **PASSED** | bracket drift 1.279 ms; first comparative window in project history to pass |
| **D** (absolute) | 30 claim members, 49/49 collected | **PASSED** | bracket drift 0.484 ms, tightest of the campaign |
| **7B floor** (`window_7bfloor_20260729`) | Qwen2.5 7B decode floor, collected 2026-07-29 | **PASSED** | CLAIM-BEARING; governed extraction clean (`all_cells_extractable` true). Floors: absolute 6.294380135190098 J, comparative 13.998036715259254 J; absolute-cell member mean 192.38623252628366 J (n=10). NOT yet minted — `MINT-GENERALIZE-01` is OPEN and unblocked as of 2026-08-02 (gauntlet closed PR #93; D-088 no-mint condition lifted), so these figures live only in prose plus the out-of-repo custody extraction until that mint runs |
| **contrast** (`window_contrast_20260730`) | 40 contrast ABBA members + 7 references, 47 bundles, 1 supersession | **PASSED** | bracket drift 1.281 ms; contrast diagnostic 146.730349 J σ 0.241 (n=10 blocks) UNGATED — MANIFEST-CONTRAST-01 closed 2026-08-02 (PR #95); the gated claim now rides `MINT-GENERALIZE-01` then the D-095 chain |

**2026-08-07 supersession (D-117):** the historical a10/re-mint and old
C/D plan are retired. Claim authority can now arise only from the
prospective alpha, beta, and gamma windows; the separately named Window C
characterization night remains Ed ruling #1. The table above is retained
unchanged as dated collection history, not present claim authority.

Window B's cause is established and is NOT a clock problem: a GPU DVFM
power ramp that the rectangular-pulse fiducial estimator aliases into an
apparent onset shift (93.28% of the drift; the wall-clock term moved the
OPPOSITE way, −0.201464 ms). D-079 clause 3 adds a pre-flight screen that
detects it in the ~4-minute pre-calibration, with cause-removal (never
outcome-selection) retry semantics.

**Corrected floor figures — the old ones must not be repeated.** a10's
**absolute** floors are **3.823787 J prefill / 3.592138 J decode**,
INCLUDING the 0.652272 J whole-window drift allowance. The 3.17 / 2.94 J
numbers circulated earlier are the attribution-width floors BEFORE the
allowance and are diagnostics only (D-079 clause 5).

**AMENDED BY D-084 (2026-07-29): `3.592138` is the ABSOLUTE COMPONENT IN
ISOLATION, not the operative decode floor.** Mint #1's cell composes
a10's absolute 3.592138 J with window C's comparative 7.377086 J, and
under W3 rule 8 the cell gate is the **max, never the sum** — so the
canonical **operative decode floor is 7.377086 J**, and that is the hard
six-decimal literal pinned in `scripts/mint_floor_artifact.py`. D-079
clause 5's "3.592138" pin predates window C's comparative extraction and
is superseded for the operative figure; both components remain published
and LABELLED per D-078 clause 11.

### The critical path: build the mint (HISTORICAL — CLOSED 2026-07-30)

All four blockers below are closed and this section is retained as
chronology only: `scripts/mint_floor_artifact.py` is the non-test call
site (1), the 30-vs-37 basis question RESOLVED (2), `production_window`
is in `_CALIBRATION_SCOPES` (3), and `impl/floor-mint` merged via PR #87
(4). Mint #1 merged via PR #88 at `da83337`.

`build_floor_cell` / `build_floor_artifact` / `build_absolute_record` /
`build_comparative_record` in `joulewise/detection_floor.py` have zero
non-test call sites; `scripts/extract_detection_floors.py` writes an
extraction report and stops. Established blockers:

1. **`claim_ready` requires an absolute AND a comparative record in the
   SAME cell**, so a10 alone mints a structurally `smoke_only` artifact.
   Mint #1 must pair a10's absolute cell with window C's decode
   comparative. Verifying that the two share backend, metric,
   `window_class`, condition family, and stack identity is a GO/NO-GO,
   not a task.
2. **A 30-vs-37 member authentication mismatch:** the a10 phase spec
   selects 30 members; the passed verdict authenticates 37. Extraction of
   the authenticated basis takes **20 min 36 s** on real data — budget
   for it.
3. **Windows C and D have no legal `calibration_scope`.**
   `_CALIBRATION_SCOPES` is `("window_a", "window_b_revalidation",
   "smoke")`. D-079 clause 4 adopts one general production name; proposed
   literal `production_window`.
4. **Pre-mint schema hardening was then written but unmerged** (it
   merged via PR #87; the branch is on main): branch
   `impl/floor-mint` @ `617060a` (pushed) makes the extraction report
   export the admissible half-widths it already computes, and moves
   `_WIDENED_FLOOR_KEYS` from optional into the required key sets so
   width ABSENCE is a schema error rather than a silent fall-back to the
   point-only floor. Suite 2198 OK.

### Disk

**EXECUTED 2026-07-28 (Ed-authorized 2026-07-27: iCloud-only acceptable,
delete after verified upload — resolving both open disk questions).**
Disk now has **115 GB free** (was 33 GB; ~61 GB freed by the repo prune described below, the rest by unrelated local housekeeping). The selective-prune plan was
generalized to every runs corpus: all 27 corpora are archived in
`~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/` with a
per-corpus `MANIFEST.sha256`. Verification before any deletion: APFS-clone
name+byte parity; `brctl evict` of 100% of files (evict success = upload
complete); rematerialize-and-rehash of 20,028 files from iCloud (100% of
small evidence files + sampled traces) against the manifests — 0
mismatches. Then 1,848 `powermetrics*.plist` traces ≈ 61 GB were deleted
locally; **every small evidence file remains resident**, each pruned dir
carries `PRUNED.md` + `MANIFEST.sha256`. Restoring any trace =
`brctl download` its path under the archive.

Kept fully local (no deletion): `runs_window_a10_20260725(+_bound)` and
`runs_window_c_20260726(+_bound)` (mint #1 inputs),
`runs_window_a5_quarantine` (quarantine is evidence), and in `runs/` the
six frozen acceptance-gate bundles (`example-mac-mlx-*`) + `experiments/`
custody — the retained-corpus strict gate re-ran green post-prune (3/3,
incl. six-bundle strict validation), and keep-list file counts verified
unchanged.

### Orchestration

Global `CLAUDE.md` hard rule 11 now defines the topology: Fable as
MAGISTRATE and Ed's direct, Opus 5 as LIEUTENANT / operational chief, a
cold-Fable-instance gate with mandatory (not discretionary) triggers, and
an enumerated forbidden-to-decide-alone list for the lieutenant. D-080's
standing fresh-eyes sweep is the first exercise of that list.

### What needs Ed

1. RESOLVED 2026-07-27/28: Ed answered both disk questions (iCloud-only
   acceptable; delete after verified upload) and the archive+prune
   executed — see "Disk" above. Note the traces are now iCloud-only
   (single durable copy); flag if a second physical copy is wanted.
2. **AC power** for measurement windows — the production policy requires
   it and the machine was on battery.
3. A magistrate ruling on a conflict between D-080 and D-061: D-080's
   anti-ritual clause 4(ii) evaluates a rotating lens against the
   two-zero-sessions drop rule, which D-061 explicitly superseded with an
   expected-loss adjudication ("three applicable exposures TRIGGER an
   expected-loss review decision, never automatic deletion").
4. `FLOOR-WORKLOAD-SIZING-01` — resizing floors resizes the science, so
   it is a pre-registration change and therefore Ed's call.
5. Window B's disposition.
6. (2026-07-28 late) Multi-session coordination: a concurrent session
   force-rewrote main history (no content lost this time, but the mode
   can silently drop peer commits). Whether to adopt a
   no-force-push/branch-only convention is Ed's call.
7. (2026-07-28 late) TEST-SPEED-01's structural lever — a PR-fast/full
   CI split — is a CI-contract change and Ed's call; the
   consolidate/redesign work (~3-4 min, no deletions) needs no ruling.

Records: `docs/run_reports/2026-07-30-mint-merge-coldgate.md` (freshest
session record), `docs/process_traces/RESUME-2026-07-28.md` (superseded
as a pointer), `RESUME-2026-07-27.md`,
`RESUME-2026-07-26.md`, `docs/process_traces/2026-07-26-prereg-clock-mitigation.md`,
`docs/run_reports/2026-07-23-window-a-collection-arc.md`, and
`docs/run_reports/2026-07-24-screen-budget-gauntlet.md`.

**Historical (2026-07-25, superseded by the block above):** main
`c3e2647` contained the merged instrument repair (PR #79) and the merged
SCREEN+BUDGET rules (PR #85); the 229-member a5-a8 collection is
non-claim-bearing diagnostic, instrument-proving evidence, and the next
claim attempt was then framed as one clean prospective quiet window per
`docs/phase_2/window_runbook.md`.

The D-078 Phase-0 instrument repair was signed off and merged through
PR #79 on 2026-07-22. Registered limitation L1 remains owned by
FLOOR-BIND-01; it does not reopen the completed repair. Record:
`docs/run_reports/2026-07-20-p0-instrument-repair.md`. Earlier arcs below
are historical.

**C-028 CLOSED (2026-07-11): the full hardening + analysis-engine arc is
on main.** Reducer lattice 0.4.2 (inter-token metric) / 0.4.1 (idle ESS,
HAC variance — local r1's 47x underestimate closed) / 0.4.0 (verdict
split + window_evidence_precheck) with frozen legacy arms; the analysis
trio complete (P2-042 manifest → P2-041 verdict split → P2-037
contrast/claim engine with unwaivable cleanup claim gating per the
two-layer waiver reconciliation); doctor preflight; publication privacy
pack (fail-closed inventory); packaging CI; primary-verified related
work; load-transition prep (B remains [QUIET-MAC]). Window A's software
gates are ALL satisfied; execution needs a quiet machine + Ed.

PRs #41-#60 form the landed C-028 arc, all merged 2026-07-11 (incl. the
#59 integration-review fixes and the #60 DOC-008 kernel refresh); none
implies live evidence. P0-003 is satisfied
by the verified iCloud backup/restore. All NVIDIA/Orin protocol pins remain
PROVISIONAL pending P1-006 live evidence.

**Historical restart snapshot (recorded 2026-07-13; non-operative).** The
numbered sequence below is retained as dated handoff narrative, not current
work-selection authority. Use the generated region above for selection.
1. DONE 2026-07-13: #61-#63 merged at delta-audited heads; site deployed
   live under the cap; XSI-1 CI hardening green on main; bridge landed
   and lead-verified (8/8 protocol checks; suite 1318 OK).
2. [ED + AGENT] **Comprehensive whole-project audit (declared gate).**
   The audit method proposal is with Ed; no further feature work, queue
   pulls, or campaign prep until the audit runs and its findings are
   adjudicated. Audit focus per Ed: overproduction (excess code/tests),
   plus everything a serious external review would check.
3. [QUIET-MAC + ED] After the audit: Window A — C-019 production-shaped
   shakedown and P2-015-SMOKE, then P2-015 floors and P2-006 baselines.
   Do not run this lane while an agent session is active.
4. [AGENT] Post-audit, outside a quiet window: P2-050 adjudication,
   SITE-02 follow-ups, P2-027 publication prep. P2-022/P2-023 remain
   blocked until the 2M corpus exists.

## Session History (pointers only — run reports own the narrative)

Parenthetical states below are historical at each report's head; they are not
current restart instructions. Current state is the CURRENT STATE block at
the top of this file.

- 2026-07-31 claims desk day (metrology suite merged via PR #90 + D-096
  window-A freeze; D-094/D-095; cooldown-join gauntlet commits 1-2 merged
  via PR #91 with DA-1 closed under the D-097 cold-gate deferral):
  `docs/run_reports/2026-07-31-claims-desk-session.md`
- 2026-07-31 contrast-window collection (`window_contrast_20260730`
  PASSED, 47 bundles) + D5-J merge via PR #89 under the D-093 cold-gate
  synthesis: `docs/run_reports/2026-07-31-contrast-window-collection.md`
- 2026-07-30 paper outline v1 archived (metrology-centric framing,
  D-091): `docs/run_reports/2026-07-30-paper-outline-v1.md`
- 2026-07-30 audit harvest → FIX-10 → escalation → cold gate (D-088) →
  PR #88 merge `da83337` (mint #1 mainline) + advisor-brief hardening:
  `docs/run_reports/2026-07-30-mint-merge-coldgate.md`
- 2026-07-30 D-080 fresh-eyes sweep memos (techniques, mechanisms,
  CV paths): `docs/run_reports/2026-07-30-sweep-techniques.md`,
  `2026-07-30-sweep-mechanisms.md`, `2026-07-30-sweep-cv-paths.md`
- 2026-07-29 modularity survey (MODULARITY-01 intake; STACK-ID-BIND-01
  claim-binding defect CONFIRMED):
  `docs/run_reports/2026-07-29-modularity-survey.md`
- 2026-07-28 (late) mint-implementation session: PR #87 hardening merged;
  mint tool built on `impl/mint-tool` (unmerged, review owed); parser
  fix D-081; pairing GO + 30-vs-37 resolved; suite-pruning consult
  (TEST-SPEED-01): `docs/run_reports/2026-07-28-floor-mint-implementation.md`
- 2026-07-28 iCloud archive + verified selective prune of all runs
  corpora (61 GB freed; keep-list intact; strict corpus gate green):
  `docs/run_reports/2026-07-28-icloud-archive-prune.md`
- 2026-07-27 evening session record (windows C/D passed; the mint is the
  critical path; D-079/D-080): `docs/process_traces/RESUME-2026-07-28.md`
  (superseded as a pointer by this file)
- 2026-07-26 evening session record (window B failed on calibration
  bracket drift; FLOOR-LABEL gauntlet parked):
  `docs/process_traces/RESUME-2026-07-27.md` (superseded as a pointer)
- 2026-07-26 session record (FLOOR-LABEL-01 in gauntlet; windows B/C/D
  planned): `docs/process_traces/RESUME-2026-07-26.md` (superseded as a
  pointer)
- 2026-07-26 pre-registered clock-pin mitigation and its outcome:
  `docs/process_traces/2026-07-26-prereg-clock-mitigation.md`
- 2026-07-18 Claude Code script bridge + native pet integration:
  `docs/run_reports/2026-07-18-claude-codex-pet-observer.md`
- 2026-07-13 Bridge v1: bridge-protocol/v1 contract + scripts/bridge tooling
  (PR #64; co-designed with Sol over the bridge itself):
  `docs/run_reports/2026-07-13-bridge-v1.md`
- 2026-07-13 Restart close: #61-#63 merged at delta-audited heads
  (DRA-001 fixed; XSI-1 CI hardening), site live under cap; audit gate
  declared: `docs/run_reports/2026-07-13-restart-merge-deploy.md`
- 2026-07-12 Claude↔Sol bidirectional bridge (concurrent Ed-directed
  thread; lead-verified 2026-07-13):
  `docs/run_reports/2026-07-12-claude-sol-bridge.md`
- 2026-07-12 Agent-lane triple: SITE-01/P2-049/P2-028 → PRs #61-#63 at
  lead-gated heads; delta re-audits owed pre-merge on #62/#63:
  `docs/run_reports/2026-07-12-agent-lane-triple.md`
- 2026-07-11 P2-041 vetted rebuild (uncommitted; lead pathspec review and
  commit pending): `docs/run_reports/2026-07-11-p2041-vetted-rebuild.md`

- 2026-07-10 NV-GATE-2 idle-capture regression debug/fix (uncommitted;
  localhost re-verification remains lead-gated):
  `docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md`
- 2026-07-10 NV-GATE-2 CODE-NOW implementation (NV-1/NV-3/NV-4/NV-5;
  live promotion evidence still gated):
  `docs/run_reports/2026-07-10-nvgate2-codenow.md`
- 2026-07-10 NV-GATE-2 accepted-findings fix round (uncommitted; merge
  metadata recreation and lead gate pending):
  `docs/run_reports/2026-07-10-nvgate2-fix-round.md`
- 2026-07-10 P2-038 accepted-findings fix round (all FIX-1..FIX-6 green;
  content-merged `origin/main`, Git merge metadata sandbox-blocked):
  `docs/run_reports/2026-07-10-p2038-fix-round.md`
- 2026-07-10 P2-038 production uncertainty software path (live quiet-machine
  closure still open):
  `docs/run_reports/2026-07-10-p2038-production-uncertainty.md`
- 2026-07-10 P2-040 reducer-version compatibility review fix (uncommitted):
  `docs/run_reports/2026-07-10-p2040-versioning-fix.md`
- 2026-07-10 P2-040 remainder implementation (uncommitted, pending lead
  pathspec commit/corpus gate):
  `docs/run_reports/2026-07-10-p2040-remainder.md`
- 2026-07-10 P2-040 / RETRO-001 fix round (committed on c027-int-p2040
  after lead review): `docs/run_reports/2026-07-10-p2040-fix-round.md`
- 2026-07-09 C-027 whole-project council review (7 gpt-5.6-sol lenses +
  counterreview + independent final examiner):
  `docs/reviews/2026-07-09-c027-whole-project-review.md` (compact run
  report: `docs/run_reports/2026-07-09-c027-council-review.md`)
- 2026-07-09 Claude Code → Codex MCP bridge hardening and live smoke:
  `docs/run_reports/2026-07-09-claude-codex-mcp-bridge.md`
- 2026-07-12 adaptive Claude Code ↔ Sol/Fable bridge follow-up:
  `docs/run_reports/2026-07-12-claude-sol-bridge.md`
- 2026-07-09 P2-034 broad campaign packs (C-026; PR #39):
  `docs/run_reports/2026-07-09-p2034-broad-packs.md`
- 2026-07-09 spec-fleshing wave 2, ultracode (C-025; PRs #33..#38;
  D-056..D-059): `docs/run_reports/2026-07-09-spec-fleshing-wave2.md`
- 2026-07-09 spec-fleshing wave 1 (C-024; PRs #29..#32; D-052..D-055):
  `docs/run_reports/2026-07-09-spec-fleshing-wave1.md`
- 2026-07-09 scientific-rigor review of suite/benchmark/question bank
  (C-023; review-only; full record in
  `docs/reviews/2026-07-09-scientific-rigor-review.md`):
  `docs/run_reports/2026-07-09-scientific-rigor-review.md`
- 2026-07-09 CP-5 resume: pre-campaign review completed, stop card
  cleared, PRs #22..#28 merged, Window-A GO
  (C-022): `docs/run_reports/2026-07-09-cp5-resume.md`
- 2026-07-09 meta-process stop-card + codex-bridge audit cleanup
  (D-050; CP-5 preserved untouched):
  `docs/run_reports/2026-07-09-meta-process-stop-card-cleanup.md`
- 2026-07-09 advisor status-site live-depth refresh (D-051/C-021;
  subordinate to the then-active CP-5 stop card):
  `docs/run_reports/2026-07-09-advisor-status-site.md`
- 2026-07-08 suite build (C-017; adjudication + PRs #17/#18/#20/#19;
  D-044..D-047): `docs/run_reports/2026-07-08-suite-build.md`
- 2026-07-08 suite-science + expansion (C-014/C-015; PRs #14/#15/#16;
  D-038..D-042): `docs/run_reports/2026-07-08-suite-science-expansion.md`
- 2026-07-08 Lakebed deploy (C-013):
  `docs/run_reports/2026-07-08-lakebed-deploy.md`
- 2026-07-08 site observatory (PR #13):
  `docs/run_reports/2026-07-08-site-observatory.md`
- 2026-07-08 critique second-pass + councils+critique (C-011 → PR #12):
  `docs/run_reports/2026-07-08-councils-critique-session.md`
- 2026-07-07/08 resume+merge (C-009 first full run; PRs #8..#11):
  `docs/run_reports/2026-07-07-resume-merge-session.md`
- Older: see `docs/run_reports/` (dated files).

## Current Verification

- **Current main: full suite `Ran 2770 tests`. The `2785` count belongs
  only to unmerged recovery commit `4495609` (15 added tests) and is
  FROZEN branch-only evidence, not a current-main result.**
- **Merged main at the PR #95 composed tree (2026-08-02, historical):
  full suite `Ran 2418 tests`, `OK (skipped=22)`, lead-run on the
  exact 94+95 integration tree merged as `200e6db`; verdict CI green
  on both merge pushes (all five jobs each).**
- Merged main `67d268a` (2026-07-31, historical): canonical `Ran 2305
  tests`, `OK (skipped=12)`, lead-run post-merge. This is the PR #91
  (gauntlet commits 1-2, DA-1 closed) merge. Branch verification chain:
  `2301 OK` at `c0adc93`, `2304 OK` at `8880395`, `2305 OK` at
  `a9b9d4a` (all lead-run, worktree skip convention 21); CI green on
  the PR (build, installed-wheel, release-chain, tests 3.11 + 3.14).
- **Merged main `7ee680c` (2026-07-31, historical): canonical `Ran 2286
  tests`, `OK (skipped=12)`, lead-run post-merge.** This is the PR #89
  (D5-J) merge; the close-out commits `49c1876`, `0d0bd0b`, `6ed1625`
  sit atop it and are docs/kernel only.
- **Merged main `da83337` (2026-07-30, historical): canonical `Ran 2280
  tests`, `OK (skipped=12)`, lead-run post-merge.** Branch head
  `16c7af0` pre-merge: lead-run `2280 OK (skipped=21)` (worktree
  convention); Sol-side `2280 OK (skipped=24)` (delegated sandbox). CI
  green on merge ref `ff0dda5` (build, installed-wheel, release-chain,
  test 3.11 + 3.14; two earlier red runs were stale-merge-ref artifacts,
  see the session report). Mint #1 `validate_floor_artifact == []`
  lead-run. Fail-open-shape corpus scans clean ×3 (magistrate, cold
  instance, refuter) across a10, window C, and the 7B window.
- **Post-prune suite on `7337b33` + docs edits (2026-07-28, lead-run):**
  `Ran 2194 tests`, `FAILED (errors=2, skipped=12)`. The two errors are
  `test_build_site_parsers` Lakebed-budget tests and are **pre-existing
  at HEAD, independent of the prune**: `32e510a` rewrote Session History
  with `docs/process_traces/` pointers, but `scripts/build_site.py
  parse_session_history` requires a backticked `docs/run_reports/...md`
  pointer in each dated bullet (verified by running the parser directly
  on the pristine HEAD file — same failure). The affected surface for the
  prune itself, `tests.test_corpus_strict_validation`, is 3/3 OK
  post-prune. RESOLVED by `cb867f3` (Ed-authored): the parser accepts
  `docs/process_traces/` Session History pointers per the
  pointer-retirement convention; `tests.test_build_site_parsers` 21/21 OK
  on that head, clearing both errors.
- **Merged main `7337b33` (2026-07-27, historical):** `FLOOR-LABEL-01`
  merged at `3055315` under the D-072 gate shape (independent Opus
  contract lens returning "comparative coverage COMPLETE" plus a fresh
  Sol xhigh audit, fix rounds each delta-re-audited, five independently
  audited correctness fixes); lead-verified suite **2194 OK** on merged
  main. Branch `impl/floor-mint` @ `617060a` (unmerged at that date;
  merged via PR #87 on 2026-07-28) records
  suite **2198 OK (skipped=24)** from that 2194 baseline plus four
  regressions. Window C's bracket drift (1.279 ms) and window D's
  (0.484 ms) reproduce from the stored `instrument_evidence.json`
  fiducial bounds in `runs_window_c_20260726/instrument_validation/` and
  `runs_window_d_20260726/instrument_validation/`.
- **Merged main `c3e2647` / PR #85 (2026-07-25, historical):** the
  SCREEN+BUDGET implementation completed four adversarial audit rounds.
  Final PR-head CI was green on all five checks (`build`,
  `installed-wheel`, `release-chain`, `test (3.11)`, `test (3.14)`).
  The final lead-side suite recorded 2141 passed / 21 skipped; its one
  battery-timing flake passed on rerun. The capsule was redeployed as
  `dep_2I04CG6tQ4t0mzY7` at 2026-07-25T01:46Z.
- **D-078 repair sign-off gate (2026-07-22, historical merged gate):**
  branch
  `impl/p0-instrument-repair` code/test head `040ca3a` (docs-only
  close-out `debc6d2` carries it unchanged; merged through PR #79):
  lead-run
  `pytest -q tests/` = **2088 passed, 15 skipped, 1570 subtests, 0
  failures**; round-9 focused review surface 357 passed at the same
  head. Entries below are historical.
- PR #65 branch `impl/bridge-v1.1` final head `8b96bd4`: canonical
  `Ran 1387 tests`, `OK (skipped=10)`, lead-run 2026-07-13 (four
  lead-side full-suite runs across the fix arc: 1371→1381→1385→1387);
  CI green on the final head (build, installed-wheel, tests 3.11 +
  3.14); `scripts/check-codex-mcp.mjs` 5/5 PASS with the v1.1 adapter;
  live session-open/close and reverse-consult probes recorded in
  `docs/run_reports/2026-07-13-bridge-v11.md`.
- Merged main `d285989` (post #65): canonical `Ran 1387 tests`, `OK
  (skipped=10)`, lead-run 2026-07-13 on the merged head;
  `scripts/check-codex-mcp.mjs` all PASS; no active workspace leases.
- Previous session (post #61-#63 merges + bridge v1 landing, pre-commit
  head `99b8640`): canonical `Ran 1318 tests in 111.017s`, `OK
  (skipped=10)`, lead-run 2026-07-13; bridge protocol checker 8/8 PASS;
  bridge focused tests 4/4 OK. Merged-main backstop at `12131b0` was
  `Ran 1314 tests`, `OK (skipped=10)`. Live capsule: measured artifact
  854,349 B deployed, routes 5/5 HTTP 200, freshness 14/14 current at
  `7d3ea57`.
- Prior head `main@194ea39` (post #59 + #60 merges): canonical `Ran 1258
  tests`, `OK (skipped=10)`, lead-run 2026-07-11 fresh-thread intake.
  PRs #41-#60 are all merged.
- Prior head `main@cc3afc3`: canonical `Ran 1220 tests`, `OK (skipped=10)`;
  retained corpus strict gate 6/6; PR #59 pre-merge lead replay was
  `Ran 1224 tests`, `OK (skipped=12)`.
- Count convention for C-028 records (SUPERSEDED — historical, applies
  only to the 2026-07-11-era tails above): ordinary worktree replays
  report `skipped=12`, final main reports `skipped=10`, and restricted
  managed sandboxes may report `skipped=13` when their environment-gated
  probe is unavailable. The CURRENT convention is the triple at the top
  of this section: main `skipped=12`, worktree `skipped=21`, delegated
  Sol sandbox `skipped=24`. Preserve those environment labels when citing
  a tail.

### Historical verification archive (exact at the recorded heads)

- P2-041 vetted rebuild: baseline canonical `Ran 1041 tests in 67.995s`,
  `OK (skipped=13)`; final focused recipe modules `Ran 398 tests in 54.964s`,
  `OK (skipped=1)`; final canonical `Ran 1062 tests in 76.436s`, `OK
  (skipped=13)`; `git diff --check` and the dead-private-helper search clean.
  The retained corpus and localhost socket gates skipped loudly; no live or
  quiet-Mac validation was claimed. Report:
  `docs/run_reports/2026-07-11-p2041-vetted-rebuild.md`.

- PR #49 P2-038 rail-only flake: pre-fix exact-test loop failed 4/100;
  retained failure emitted `cadence_ratio_unrecorded` plus
  `interpolation_bound_unrecorded` because the final trace sample preceded the
  stop marker. Archived `origin/main` reproduced on iteration 6. The
  fixture-only terminal-sample handshake fix passed the exact test 100/100,
  focused module `Ran 5 tests in 30.480s`, `OK`, and canonical suite
  `Ran 1041 tests in 66.509s`, `OK (skipped=13)`. Report:
  `docs/run_reports/2026-07-10-pr49-p2038-flake-root-cause.md`.
- NV-GATE-2 idle-capture regression fix: historic fake-sampler plus new
  delayed-readiness regression passed together in 3 consecutive fresh
  processes; canonical suite `Ran 1023 tests in 35.164s`, `OK (skipped=13)`;
  `py_compile` and `git diff --check` clean. The exact localhost contract was
  attempted 3 times but loudly skipped before worker execution because this
  sandbox denied socket bind; lead socket-capable 3x rerun remains required.
  Report: `docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md`.
- NV-GATE-2 accepted-findings fix round: focused node-worker/subprocess,
  controller, reducer, strict-dispatch, and schema surface `Ran 229 tests in
  4.995s`, `OK (skipped=2)`; the historic fake-sampler test passed three
  consecutive fresh-process runs; canonical suite `Ran 1022 tests in 34.406s`,
  `OK (skipped=13)`; targeted `py_compile` and `git diff --check` clean. The
  0.3.1 dispatch came from `origin/impl/p2040-remainder` because post-main did
  not contain it. Report: `docs/run_reports/2026-07-10-nvgate2-fix-round.md`.
- NV-GATE-2 CODE-NOW worktree: baseline `Ran 910 tests in 32.549s`,
  `OK (skipped=12)`; final canonical suite `Ran 922 tests in 33.551s`,
  `OK (skipped=13)`; focused NV-1/NV-3/NV-4/NV-5 surface `Ran 232 tests
  in 6.085s`, `OK (skipped=2)`; `git diff --check` and targeted
  `py_compile` clean. The added skip is loud and specific: this managed
  sandbox denied localhost socket bind for NV-5. No live NVIDIA evidence or
  de-provisionalization was claimed.
- P2-038 accepted-findings fix round: all FIX-1..FIX-6 complete; focused
  `Ran 70 tests in 41.211s`, `OK`; canonical `Ran 992 tests in 68.140s`,
  `OK (skipped=12)`; `git diff --check` clean. The real-child rail-only path
  now withholds drift on unknown contamination while gross remains eligible;
  P2-039's pending guard validator accepts the emitted block; backup launch
  failure, extreme-sentinel exclusion, child invocation, and literal phase
  constants are regression-tested. The absent worktree `runs/` corpus produced
  the loud six-bundle acceptance-gate skip. Git merge metadata remains absent
  because the managed sandbox cannot write the external worktree admin dir;
  the exact clean three-way `origin/main` content snapshot is applied.
- P2-040 reducer-version review fix: focused strict/reducer run
  `Ran 84 tests in 1.908s`, `OK`; extended strict/reducer/schema run
  `Ran 104 tests in 1.997s`, `OK (skipped=1)`. Canonical run reached
  `Ran 926 tests in 33.732s`, `FAILED (failures=1, skipped=12)` solely at
  pre-existing `test_telemetry_measure_idle_with_fake_nvidia_smi`; isolated
  reruns reproduce its 0.2-second fake-process timing failure. All
  reducer/version tests pass; no out-of-scope node-worker change was made.
- P2-040 remainder worktree: pre-change baseline `Ran 910 tests in 34.584s`,
  `OK (skipped=12)`; post-change focused affected modules `Ran 256 tests in
  3.744s`, `OK (skipped=1)`; canonical `Ran 924 tests in 32.812s`, `OK
  (skipped=12)`; compileall and `git diff --check` clean. The unchanged
  six-corpus test produced its required loud skip because `runs/` is absent;
  lead 6/6 strict read-only rerun remains the landing gate.
- P2-042 emitter branch `impl/p2042` (lead-committed base; draft PR #46;
  targeted-review fix round complete in the worktree, no fix-round commit):
  FIX-1 fail-closed typed identity/linkage validation, FIX-2 semantic
  `run_id` derivation, and FIX-3 raw-byte AP hashing/LF config emission are
  implemented. Focused manifest/generator/campaign checks: `Ran 82 tests in
  12.317s, OK`; final canonical suite: `Ran 989 tests in 33.405s, OK
  (skipped=12)`. Review regressions cover `run_id=[]`, one malformed identity
  at each manifest object layer, a fully rehashed coherent rename, and a CRLF
  AP fixture. Report:
  `docs/run_reports/2026-07-10-p2042-analysis-manifest.md`.
- P2-040 reducer-version review fix: focused strict/reducer run
  `Ran 84 tests in 1.908s`, `OK`; extended strict/reducer/schema run
  `Ran 104 tests in 1.997s`, `OK (skipped=1)`. Canonical run reached
  `Ran 926 tests in 33.732s`, `FAILED (failures=1, skipped=12)` solely at
  pre-existing `test_telemetry_measure_idle_with_fake_nvidia_smi`; isolated
  reruns reproduce its 0.2-second fake-process timing failure. All
  reducer/version tests pass; no out-of-scope node-worker change was made.
- P2-040 remainder worktree: pre-change baseline `Ran 910 tests in 34.584s`,
  `OK (skipped=12)`; post-change focused affected modules `Ran 256 tests in
  3.744s`, `OK (skipped=1)`; canonical `Ran 924 tests in 32.812s`, `OK
  (skipped=12)`; compileall and `git diff --check` clean. The unchanged
  six-corpus test produced its required loud skip because `runs/` is absent;
  lead 6/6 strict read-only rerun remains the landing gate.
- P2-040 / RETRO-001 fix-round worktree: canonical suite `Ran 908 tests in
  32.723s`, `OK (skipped=11)`; focused 211 tests OK; claims lint exit 0 with
  no errors; `git diff --check` clean. The absent `runs/` corpus produced the
  required loud six-bundle acceptance-gate skip; the lead corpus gate then
  PASSED (6/6 strict via corpus symlink), plus mock e2e run+strict+reduce
  and the post-merge full suite (OK, skipped=12).
- **2026-08-07 tool-version note:** this document does not assert the current
  installed tool versions; verify them directly before protocol use. The
  following result is retained as historical verification context.
- Claude Code 2.1.207, Codex CLI 0.144.0, and Node 23.7.0 pass the
  bidirectional protocol checker. Claude → Sol now uses `gpt-5.6-sol` with
  `high` fallback/default and task-triggered xhigh/ultra escalation; the
  final guarded `/codex` smoke returned `JOULEWISE_SOL_HIGH_GUARDED_OK`
  (thread `019f5a2a-2f4a-7b33-8a6d-b44dcc5a7a26`) with source `mcp`, effort
  `high`, read-only sandbox, and `on-request` approvals. Claude-originated
  Sol sessions disable the reverse server. Top-level Sol → Fable uses the
  sole `consult_fable` MCP tool; live token `JOULEWISE_FABLE_MCP_OK` on
  thread `019f5a26-d8a6-7993-b48d-8131d88748b9`. Focused bridge tests pass
  4/4 and `gen_state.py --check` passes. The current full suite ran 1,317
  tests but is not green: one failure + one error in `test_gen_state` are
  caused by the concurrent uncommitted state-kernel removal of `P2-028`
  while the existing fidelity tests still require that ID; bridge tests are
  unaffected. Full details: `docs/run_reports/2026-07-12-claude-sol-bridge.md`.
- Last code-bearing verified head c095c83 (post PR #39; note: 36d5641
  later changed `scripts/build_site.py` on main without a recorded
  verification — flagged by C-027, covered by RETRO-001): suite `OK (skipped=10)` and
  repo lint errors=0, lead-run; pack lint errors=0 warnings=0.
- Prior: main after wave-2 integration fixes: `python3 -m unittest discover -s
  tests` → `Ran 877 tests, OK (skipped=10)`, lead-run; repo lint
  errors=0; CI green on all six PR heads (#33..#38); combined-ref
  pre-merge suite check green; live rotated mock campaign strict-valid
  with order provenance (lead-validated); mock e2e emits uncertainty
  fields per D-057.
- Prior: series head f75134d (post PRs #29..#32; docs-only) lead-verified;
  integration-fix commit 7156295 is also docs-only (no test surface):
  `python3 -m unittest discover -s tests` → `Ran 822 tests, OK
  (skipped=10)`, lead-run; CI green on all four PR heads (py3.11+py3.14);
  integration reviewer independently re-ran the suite and recomputed the
  detection-floor campaign arithmetic.
- Prior verification (7666652, post PRs #22..#28): `Ran 822 tests, OK
  (skipped=10)`, lead-run.
- Live lead gates this session (real MLX, Qwen2.5-1.5B via `.venv`, mock
  telemetry): single-prompt + TWO full 48-item jw_mixed suite runs
  (pre-merge old manifests, then final merged main with the REGENERATED
  manifests) — all strict-valid; 48/48 hash-domain closures on the
  real tokenizer; output token ids, model artifact hash, pinned sampler,
  and package versions verified present in the bundles.
- Envelope gate live: honest `envelope_failed[E1]` on the mock affine
  bundle; refusals for wrong-profile/malformed/mixed inputs; exit codes
  0/2/3.
- Bundle pack live: pack → verify(0) → tamper → verify(2).
- Manifest regen: byte-identical double-regen; all realized counts 512;
  new effective shas 855be4e5 (mixed) / 0316283d (sentinel).
- CI green on every merged head (PR #27's first merge-ref run failed on
  a cross-branch fixture interaction; fixed test-side, then green).
- Post-merge integration reviews (both waves): CLEAN, incl. an
  end-to-end mock campaign → strict → envelope-gate → pack → verify flow
  and a D-033 legacy-identity spoof probe that failed closed.
- `validate-bundle --strict` green over all 6 real corpus bundles under
  the new era rule (PR #22 live gate: 6/6 valid, tamper fails named).

## Known Workspace State

- (2026-08-16 T9 close, CURRENT) `main` and `origin/main` at the T9
  close-and-sweep head (see the T9 checkpoint above); the worktree is clean.
- (2026-08-08 night, historical) `main` and `origin/main` were
  both at `4c6a8fb558d7b979672dd4244efc797689785548`.
- (2026-08-02, historical) `main` and `origin/main` at `bcbc10b`; working
  tree clean except the untracked private `CLAUDE.local.md` (Ed's;
  never commit) and `.desk/` (adjudication custody; never commit).
  PR #93 merged (the c3 branch is closed). Branch
  `impl/d100-bii-binding` exists in the session worktree
  `scratchpad/d100bii` holding the UNCOMMITTED, audit-pending
  D100-BII-BINDING-01 diff (envelope protocol failure; see §9).
- (2026-07-31, historical) `main` and `origin/main` were both at `6ed1625`:
  the PR #89 merge `7ee680c` (D5-J) plus the close-out commits
  `49c1876`, `0d0bd0b`, and `6ed1625`. Branch `impl/mint-tool` is MERGED
  (verified `git merge-base --is-ancestor impl/mint-tool main`), as are
  `impl/floor-mint` and `impl/floor-label-clean`; all three may be
  deleted. Their scratchpad worktrees are still registered (`minttool`
  plus ~11 review/pin worktrees under the `9c166892…` session dir, and
  prunable entries under `ad48bfae…` and `d714f367…`) — `git worktree
  prune` plus explicit removal is owed as housekeeping. The working tree
  is clean except for the untracked private `CLAUDE.local.md` (Ed's
  file; never commit it).
- (2026-07-28 late, historical) `main` and `origin/main` were at that
  session's bookkeeping commit atop the PR #87 merge `058c918`. Branch
  `impl/mint-tool` (pushed, then UNMERGED) held the 9-commit mint series
  `2a0ecbc..697f741` in worktree
  `/private/tmp/claude-501/-Users-edr-code-JouleWise/9c166892-d763-42c4-8cf7-383912f054c9/scratchpad/minttool`;
  canonical suite at its head `1d83d68` is UNVERIFIED (rerun was in
  flight at checkpoint). Branch `impl/floor-mint` is merged via PR #87
  and may be deleted. NOTE: a concurrent session force-rewrote main
  history this evening (content preserved; see run report Anomalies) —
  verify `git log` freshness before building on a cached head.
- (2026-07-27, historical) `main` and `origin/main` were at `7337b33`. Branch
  `impl/floor-mint` @ `617060a` is pushed and NOT merged; it carries the
  pre-mint floor schema hardening. Window C (+bound) and a10 (+bound)
  remain FULLY resident in the working tree (mint #1 inputs); windows B/D
  and all other runs corpora are locally pruned to small evidence files
  (traces archived + verified in iCloud, see "Disk" above), and custody
  material lives OUTSIDE the repo at `~/JouleWise-window-custody/` — an
  agent searching only the repo will wrongly report quarantined evidence
  missing. Disk has 115 GB free; a window writes ~6 GB. The next quiet-window operator must start
  from a separate clean, merged-main measurement checkout per
  `docs/phase_2/window_runbook.md`.
- The generated state-kernel regions in this file and `TASK_QUEUE.md` are
  IN SYNC with `docs/process/state_kernel.json`
  (`python3 scripts/gen_state.py --check` exits 0), and the kernel's own
  content was last refreshed at the T9 close (stamped `updated: 2026-08-16`,
  `latest_report` → `docs/run_reports/2026-08-16-t9-session.md`); the
  2026-08-01 refresh below is historical: the MET
  rows are folded in, the completed
  `FLOOR-LABEL-01`, `STACK-ID-BIND-01`, `P2-015`, and
  `COOLDOWN-JOIN-DA1-01` rows are retired to
  `TASK_QUEUE.md`'s completed table, and the post-mint intake
  (`COOLDOWN-JOIN-GAUNTLET-01`, `MINT-GENERALIZE-01`,
  `MANIFEST-CONTRAST-01`, `SUPERSESSION-DUP-REFUSAL-01`,
  `QA-10A-JOIN-OMISSION`, `QA-10B-EXISTING-RETRY`) is folded in. Any
  further change means editing the kernel and then running
  `python3 scripts/gen_state.py` — never hand-editing the generated
  regions.
- (2026-07-25, historical) `main` and `origin/main` were at `c3e2647`,
  the PR #85 merge; PR #79's repair and PR #85's SCREEN+BUDGET
  implementation both landed with green final PR-head CI.
- The generated state-kernel blocks are authoritative for work selection.
  Hand-authored `RUN_STATE.md` and `TASK_QUEUE.md` text remains authoritative
  only for its own factual, policy, and historical domains;
  `docs/decision_log.md` remains the policy authority, exit checklists own
  phase completion, and evidence artifacts own scientific truth.
- Retained corpus and session scratchpad evidence are immutable.

## Historical Next-Work Snapshot (superseded 2026-07-15)

The following 2026-07-13 narrative is retained for chronology only. It is not
a live queue or restart instruction; the generated work-selection region is
the sole selector.

The comprehensive whole-project audit is the declared gate (Ed,
2026-07-13): method proposal pending Ed's approval, then the audit runs
and its findings are adjudicated before any further feature work. After
that: Window A in the first clean quiet-machine window (C-019/P2-015-SMOKE,
then P2-015 floors, P2-006 baselines), with post-audit [AGENT] heads
P2-050 adjudication, SITE-02, and P2-027 publication prep outside quiet
windows. `TASK_QUEUE.md` remains the ordering authority.

Hardware-gated (unchanged): 2K/2L (P1-006; NV-GATE-2 additions from
C-027 apply at live promotion), wall meter (P1-003), topology (P1-004),
calendar mapping (P1-008).

## Reference Decisions And Blockers (non-selection context)

These pointers retain external-dependency context but do not rank or select
work. The generated region controls task selection.

- Supervisor approval and scope pending (P1-001, R-001 — mitigation
  holding); gates FULL D-016 closure.
- Calendar dates pending (P1-008, R-012).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).
- Git author identity on this machine auto-selected as
  `Ed R <edr@Eds-MacBook-Pro.local>`. Amend future commits if a
  different identity is needed.
