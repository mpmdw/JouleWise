# Synthesis-time cure exhibits (post-freeze; packet bytes unchanged)

Both cold judges ruled the packet FROZEN bytes stand and named cures
deliverable at synthesis. Per the bootstrap rule, the packet itself is
not edited; these exhibits cure the named defects in the synthesis
record only.

## SX1 — Queue row A52 verbatim (cures judge-A/B Q2b REFUSE)

Source: `TASK_QUEUE.md` at immutable revision `2297cf0` (current main
at exhibit time), line 449. Its exact words are the object of Q2b
("as drawn"). Why no other primary evidence: the row IS the drawn
text.

> | A52 | D080-TRIGGER-01 | P3 Hardening Candidates | BLOCKED —
> D-080-amendment (Ed ratifies the trigger cadence and the runner
> (cron routine vs manual)) | Wire D-080's standing fresh-eyes sweep
> to a REAL trigger (calendar cron or every-N-merged-PRs), run as a
> separate concurrent read-only instance per the Ed-validated
> 2026-08-03 pattern, findings delivered mid-flight; reconcile D-080
> clause 4(ii)'s stale zero-unique-catch citation. | ...
> (acceptance/authority cells elided; full row at
> TASK_QUEUE.md:449@2297cf0)

Note for synthesis: the row's block condition names TWO legs — the
trigger cadence AND the runner (cron routine vs manual). R1
ratification supplies the cadence SHAPE only; the numeric backstop,
the mechanical definitions (judges' M2), and the runner choice remain
open, the runner being expressly Ed's. Queue-hygiene NIT: the same row
appears twice (TASK_QUEUE.md:374 and :449, near-identical) — dedup in
the next queue pass.

## SX2 — Sol full-shadow dissent: corrected provenance (cures judge-B M3)

The packet's §8 attributed the dissent to E3. Corrected record:

1. The dissent's PRIMARY record was thread `019fca7c`, lost to MCP
   recycle before persistence (acknowledged in the packet's E2
   description).
2. Surviving secondary evidence: (a) the lead's contemporaneous recap
   embedded in the E3 session's AUTHORITY block — "compressed shadow
   with rollback (Ed-ruled; your full-shadow preference recorded as
   dissent)" (rollout `019fcafc`, pinned sha `f22e48da…`, user turn
   4) — which Sol read and did not contest; (b) E3's own final
   message, whose recorded position is CONDITIONAL soundness of the
   compressed story ("sound only if the rollback recipe and handoff
   are accessible outside t3 before quitting, the previous plane
   remains usable, and no real repository write occurs before the
   isolated-native-write gate") plus seven material corrections — not
   full-shadow advocacy.
3. The synthesis therefore records the dissent as: "Sol initially
   preferred a full shadow period (lost-thread record, uncontested
   recap); its surviving recorded position is conditional acceptance
   of the compressed cutover with corrections, all of which were
   adopted into the night plan." Judge B's observation stands: the
   packet overstated, not understated, the opposition.

## SX3 — B1-gate contamination disclosure (retroactive, same class as judge finding B1)

The CAL-BRACKET B1 gate's cold Fable judge (earlier tonight,
`docs/process_traces/2026-08-03-calbracket-b1-gate/ruling-cold-fable.md`)
was launched the same way — subagent in the main checkout — and
therefore had the same doctrine/memory auto-injection the doctrine
judges disclosed. It made no disclosure (its convening predates the
charter's disclosure duty). Mitigations of record: its ruling cites
file:line evidence it personally verified for every load-bearing
conclusion, and its core findings were independently confirmed by the
Sol refuter at the same head. Disposition: the B1 gate's outcome
stands on its evidence; the contamination is disclosed here and in an
erratum note in that gate's synthesis; all future cold convenings
follow the registry's clean-launch procedure adopted tonight.

## SX4 — Phone-gate custody cure (answers refuter BLOCKER "keep the phone-approval gate open")

Harness-event timelines extracted by the lead from the probe threads'
transcripts (the exact "custody-pinned harness event and filesystem
timeline" the refuter required):

APPROVED thread `9e9707d1-7165-4e15-b84c-27107d5b83e9`
(sha256 f86a4cb526b87661075af111a1674eb994fa7c81205cebd46630de62428f7614):
- 05:25:25Z user probe prompt; 05:25:29Z model tool_use (the write)
- 05:27:34Z tool_result exit=0 — a 125 s HOLD between call and
  execution; file mtime 22:27:34 local == 05:27:34Z: execution at
  release, to the second. Resolves the refuter's "write ~11 s before
  tap" reading — Ed's 22:27:45 was clock-reading lag; the harness
  event is authoritative.
- 05:27:37Z second tool_use (stat); 05:28:24Z result — 47 s hold
  (the second card).

DECLINED thread `c8b0cf1c-b48f-452c-932f-eca40f6dd38e`
(sha256 1efb640bd1f44645a7fc50b80e6b96b7b7c9ce1a8fd0fb3a59eb18bcfe83a08b):
- Two probe attempts, both writes REFUSED by Ed's decline; harness
  returned "user doesn't want to proceed"/"User declined tool
  execution" to the model; no file write occurred from this thread.

Together: Supervised ("approve actions") holds execution until tap,
declines block entirely, and the model remains blind to the layer
(its own reply claimed "no permission prompt"). Two-sided,
custody-pinned, operator+filesystem+harness triangulated.

## SX5 — Ed operator ruling (2026-08-03 ~23:20, in-session, binding on amendment drafting)

Verbatim: "when im running t3 i want it to be my main driver but dont
codify it past that like if i happen to be using claude code doing be
like polluting context with t3 stuff."

Effect: the rule-11 amendment frames t3 as the PREFERRED PRESENTATION
PLANE WHEN IN USE — not a mandatory or exclusive plane. Plain
claude-code sessions remain first-class; t3-specific ceremony
(ingestion notes, thread-mode rules) binds only t3-mediated activity.
Converges with the refuter's rejection of over-broad codification
(Q1e narrowing, Q4 qualifier).
