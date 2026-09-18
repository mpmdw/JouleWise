# Exhibit F — what cold-gate ruling 70 already decided, and what it left to mechanism

Cold-gate 70 ruled on the same lane eight hours earlier. Its outputs are
tracked in this repository under
`docs/process_traces/2026-09-17-interactive-5c919872/70-coldgate-packet-quiet-admission/`.
This exhibit reproduces the two places that bound what packet 71 may ask,
byte-exact via `nl -ba <file> | sed -n '<a>,<b>p'`. Line numbers are each
file's own.

## F1. The verdicts in force, per question

Source: `13-magistrate-synthesis-ruling-70-with-opus-amendments.md:1-18` — the
synthesis header (naming its two inputs) and the verdict table entire, Q1
through Q10, so no row is quoted apart from the others. Q10's row is the one
Q3 of this packet depends on.

```
     1	# Magistrate synthesis of cold-gate ruling 70 with the Opus pairing refuter's amendments (interactive session 5c919872, 2026-09-17 ~20:5x PDT)
     2	
     3	Inputs: `10-coldgate-fable-ruling.md` (cold Fable judge, sha256 b5c08240…), `12-opus-pairing-refuter-on-ruling-70.md` (Opus, contract lens, formed by re-reading every cited line), exhibits A–G. The magistrate decides where the two disagree and records dissent; nothing here amends a rule.
     4	
     5	## Verdicts in force, per question
     6	
     7	| Q | In force | Source | Binding consequence for NIGHT-GATE-QUIET-ADMISSION-01 |
     8	|---|---|---|---|
     9	| Q1 | AFFIRM | ruling §3, confirmed | first sample AT t0; wait is plan data in a NEW plan; the GO receipt must state that admission evidence is not capture evidence (a required receipt field plus a contract-doc sentence) |
    10	| Q2 | AFFIRM (contingent on Q4) | ruling §4, confirmed | consecutive-count stays plan data |
    11	| Q3 | AFFIRM, conditional | ruling §5; refuter: within charter | the load veto is removed only in a v4 plan whose interval-CPU cutoff has been affirmed by a later gate; load stays a diagnostic on every sample and receipt; v2 semantics untouched |
    12	| Q4 | REFUSE | ruling §6; all four joule figures re-derived by the refuter | no cutoff value may be activated; mechanism may land with the value as plan data and no admitting default; the cure is the joule campaign in lane QUIET-PREDICATE-EVIDENCE-01 (kernel 232), scoped by ruling §6 items 1–4 with the slot budget corrected to 480 s |
    13	| Q5 | AFFIRM, conditional | ruling §7; refuter: the 0.217 cpu-s round excluded the census probe | the observer floor (0.0072 core per 30 s) is provisional; the seat's live sampler smoke must include the census probe in the measured cost; no cutoff derivation may quote the floor until re-measured with the census included (folded into lane 232) |
    14	| Q6 | AFFIRM | ruling §8; refuter: the per-sample fresh-census condition exceeds the proposition | the magistrate ADOPTS fresh census on every sample as a mechanism choice (it is what the brief's D3 already specifies and what D-181's "census at t0" implies for a t0 that is now an interval); recorded as the magistrate's choice, not a ruled requirement |
    15	| Q7 | AFFIRM | ruling §9, arithmetic confirmed | generator validates `window_max_s ≥ bind_max_s + post_bind_budget_s` and `post_bind_budget_s ≥ 7980` from the constants |
    16	| Q8 | AFFIRM as design | ruling §10, schema ids confirmed unoccupied | binds the seat to regression 7 (byte-identical v2, no default insertion) |
    17	| Q9 | REJECT → superseded | ruling §11 rested on exhibit E, which omitted the 2026-09-16 amendment (lane record 06 lines 44–61) where Ed had already ruled part (b); refuter: should have been REFUSE under charter §4 | the packet defect is the magistrate's; recorded in D-182's provenance paragraph. Ed re-affirmed the consolidated rule on 2026-09-17 ("affirm of course"), extended to bind-window expiry; PR #357 records it as D-182. Stage D7 of the seat may land only after #357 merges |
    18	| Q10 | four items named | ruling §12; refuter refutes item 3's reasoning | item 1 (0.05 placeholder) accepted: no candidate value in generated plans, fixtures or docs; item 2 (D7) accepted, gated on #357; item 3: reusing `night_refused_not_quiet` classifies identically under `arm_retry.DISPOSITIONS` (refuter, `arm_retry.py:74-79,90`), so a distinct code is NOT required by contract — the magistrate still chooses a distinct code `night_refused_bind_expired` as a mechanism choice (the published description string at `:31` is what changes, and a refusal that waited ten minutes is not the same event as a one-shot refusal); item 4 (R1 text) accepted, gated on #357 |
```

The same file's remaining sections — the seven corrections the seat had to
apply, the dissent record and the packet-assembly lessons — are lines 20-37 and
are reproduced so the table is not read without what follows it:

```
    20	## Corrections to the brief (exhibit G) the seat must apply
    21	
    22	1. A capture slot's budget is 480 s (`scripts/gen_derivation_night.py:88`), not 60 s; every joule sentence in the contract doc uses 480 s and the ≈1 J / ≈5 J bars from D-078 cl.11.
    23	2. No candidate cutoff anywhere: the `--quiet-admission-json` input carries the value; fixtures used for plan validation carry `busy_core_max: 0.0` (admits nothing); tests of the GO path inject their own values inside the test; the contract doc names no number and says the value awaits lane 232 and a gate.
    24	3. A required non-empty `cutoff_authority` string in `quiet_admission` (the record path of the gate that affirmed the value); validation refuses an empty string; test fixtures use the literal `TEST-ONLY-NOT-A-RULING`.
    25	4. Bind-window expiry refuses with the distinct code `night_refused_bind_expired`, registered in `NIGHT_DRIVER_REASON_CODES` and in `arm_retry.COLD_GATE_CODES` (same class as `night_refused_not_quiet`; no new remedy text).
    26	5. Receipt v3 carries `admission_is_capture_evidence: false` and the contract doc states in one sentence why (reservation then a 600 s settle follow GO).
    27	6. Stage D7 (successor route, R1 sentence, `COLD_GATE_CODES` description) is HELD on the branch until PR #357 (D-182) merges; the seat implements it behind that gate as its own final commit so it can be dropped or kept without touching D1–D6.
    28	7. The live sampler smoke measures the sampler's own cost WITH the census probe included and reports it.
    29	
    30	## Dissent recorded
    31	
    32	None between the magistrate and the refuter. The judge's Q9 verdict is not overruled; it is superseded by evidence the judge was not shown, and by Ed's re-affirmation.
    33	
    34	## Lessons for the packet assembler (the magistrate owns them)
    35	
    36	- An excerpt of a record must run to the record's end or state what follows; a lane record's "awaiting ruling" status can be amended below it.
    37	- Every claim in a brief that carries a number (the 60 s slot) gets the same first-use verification as a code citation.
```

## F2. Ruling 70 §12 — the mechanism list, including "sampler supervision"

Source: `10-coldgate-fable-ruling.md:78-84`, the cold judge's own Q10 section
entire. The final line is the one consult 19 cites as its authority for
redesigning the transport without a further ruling (exhibit A §A3,
`Authority`).

```
    78	## 12. Q10 — exhibit G items that exceed mechanism choice
    79	
    80	1. `busy_core_max: 0.05` in fixtures, docs and any generated plan: a threshold value, and a different one from the consult's 0.01. Even labelled placeholder it is not the magistrate's; fixtures must carry a value that admits nothing until Q4 is cured.
    81	2. §D7 entire: `zero_capture_successor_allowed`, the new R1 sentence, and rewriting `COLD_GATE_CODES["night_refused_not_quiet"]` (which `render_policy` publishes into the handback). Process rule (Q9).
    82	3. Reusing reason code `night_refused_not_quiet` for bind expiry: it feeds the retry classification table, so it is contract, not journal representation; a distinct code or an explicit ruling is required.
    83	4. Editing NIGHT_HANDBACK R1 (`:134-142`) at all: A172 ruling text.
    84	Mechanism, within the magistrate's discretion: factoring `evaluate_night`, the sample journal, receipt v3 fields, sampler supervision, `_artifact_list`, generator flag, the `:59` "85 minutes" correction (code already derives `t0−600`, `run_night.py:1415`, `magistrate_watchdog.py:86`; land it as its own commit).
```

Ruling 70's own packet-hygiene section, `10-coldgate-fable-ruling.md:86-94`, is
included because it is that judge's assessment of the assembler of this packet:

```
    86	## 13. Packet hygiene
    87	
    88	- Compound/ambiguous Q4: two candidate cutoffs (0.01 A; 0.05 G) and no single "proposed" value; the summary does not flag the discrepancy. Effect: Q4 REFUSE.
    89	- Unsupported arithmetic: exhibit G's "60 s capture slot"/"300 J" understates a slot by 8× (480 s). The packet repeats the ≈5 J bar without the slot duration. Effect: Q4.
    90	- Incomplete for Q5: no observer-cost measurement anywhere; supplied here by my probe.
    91	- Incomplete for Q9: the pre-registration's "no-retry conditions" (`:78`) is not excerpted in F6 though it is contrary evidence.
    92	- Convening apparatus not frozen: `01-convene-script.sh` is modified and uncommitted in this worktree (checkout reference changed from `a90ab4e8` to `80ff3a01`); the packet and exhibits are digest-pinned and unaffected. NIT.
    93	- Narrative excerpts (B3, B4 lines 25/47, E4, F3) are labelled and bounded; I verified E4 `:36-40`, B4 `:47` and F3 `:145-147` byte-for-byte at their stated lines and read nothing beyond them, so surrounding neutrality is unverified. B4's "85–100 % CPU" is a decaying `%CPU` reading, the metric the consult disqualifies; the cumulative-CPU-minutes figure is the sound part.
    94	- Neutral otherwise: contrary evidence (two of four nights not load losses) is stated; D-181's opposing clauses are quoted whole.
```
