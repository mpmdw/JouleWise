# Cold gate QPE-SHAPE3-NIGHT-BLANK-01: does one shape-(iii) envelope blank a quiet-predicate night?

You are a COLD judge: a fresh session with no loop context. Your working tree is a detached checkout whose code is identical to main `1417c0c4` (BFG-S S0 merged; S2 not yet written). Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory or skill files. **Write the contamination disclosure first.**

## Why you are convened

The BFGS-DESIGN-01 addendum-3 erratum judge wrote this flag in its §6 without ruling on it, because it was outside that charge:

> under text 6's "blank on non-pass", a single shape-(iii) envelope (one timed-out collector) blanks the whole night's numbers, whereas a collector that crashed before writing anything is excluded and the night proceeds. Both are ruled behaviour and no number escapes either way, but the asymmetry is the v1.1 blocker-1 shape at the status level; if the magistrate wants a shape-(iii) envelope excluded as `collect_error` instead, that is a text-6 change for a cold gate, not a bench fix.

The magistrate may not amend text 6 alone. S2, which implements text 6 in `pilot_summary` and `summarize`, is not briefed until this is ruled.

## The magistrate's bench facts (verify them, do not trust them)

- F1. `joulewise/quiet_predicate_campaign.py:1566-1567`: the executor waits `envelope_s + 30` for each collector and books `code = 124` on `TimeoutExpired`. `cleanup_groups` then reaps the group. A timed-out collector is killed mid-envelope.
- F2. `:1150-1151`: `pilot_summary` today appends `collect_error` to `excluded` for every entry with `collector_exit != 0`. So today one timed-out envelope costs only its own admission, and the night proceeds.
- F3. `scripts/sample_quiet_predicate_evidence.py`: the capture path's first `session.json` write (`:1084`) happens before any round. `end_stamp` is set only in the `finally` block, and the final write (`:1208`) is the only one that carries it. So a collector killed between those points leaves shape (iii) under amendment 30: `session.json` present, `end_stamp` absent, and a non-refusal `error_class`.
- F4. Under text 6 and amendment 32 (erratum), such an envelope is not in amendment 32's step-(1) carve-out, because `session.json` exists. `authenticate_quiet_session` runs on it. Amendment 30 gives `battery_float_evidence_missing` / `quiet span unavailable` unless rung (b) raises first. Text 6 then blanks the whole night: `retained`, pairs, sizing, spreads, and every `joules`/`combined_joules`/`interior`.

## Packet (absolute paths)

- Text 6 and the rest of Final texts v1.1: `/Users/edr/code/JouleWise-wt-bk-e6f06c96/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md` §4 (text 6 is under B).
- The erratum (amendments 26 and 29–34, the class rule, and the §6 flag): `/Users/edr/code/JouleWise-wt-bk-e6f06c96/docs/process_traces/2026-09-26-activation-f8d6cab1/10-s0-delta/20-coldgate/30-erratum/21-coldgate-fable-erratum-ruling.md`.
- The v1.1 blocker-1 the flag refers to: the refuter and ruling files in `/Users/edr/code/JouleWise-wt-bk-e6f06c96/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/` (`11-opus-contract-refuter.md`, `30-addendum/21-...`).
- The code in your working tree: `joulewise/quiet_predicate_campaign.py` (`pilot_summary`, the executor loop), `scripts/sample_quiet_predicate_evidence.py` (`collect`, `summarize`), and `joulewise/battery_float.py` (`authenticate_quiet_session`, as merged in S0).

## Questions to rule

1. **Shape (iii) with `collector_exit != 0`.** KEEP text 6 (blank the night), or AMEND so the envelope is excluded as `collect_error` (already in the frozen vocabulary; registration digest `69321c69…` unchanged) and the night proceeds, with its battery verdict still listed in `battery_float_envelopes`. Or some other text you design.
2. **The pre read inside that envelope.** If you amend: does a `confounded` pre read (the battery was charging at that envelope's start) still blank the night, or does only the missing post read get excused? Rule on the science. Each other envelope carries its own pair, but the night's numbers are pooled.
3. **Custody.** Confirm that rung (b) (`CustodyFailure` on a raw digest mismatch) and every amendment-29/30 raise still apply before any exclusion. No exclusion may swallow custody.
4. **Shape (iii) with `collector_exit == 0`.** Can it occur honestly? If it can, how is it treated?
5. **`summarize`.** It has no executor entry and so no `collector_exit`. What does it do with a shape-(iii) session?
6. **Tests.** Defect-shaped T6 rows for S2, each naming the counterfactual input and the production call site (`pilot_summary` / `summarize` → `authenticate_quiet_session`), with the expected RED against a naive implementation of text 6 as it stands.

Weigh campaign cost (one slow `log show` or a sampler stall costs a whole night) against the conservative reading, and against the erratum's own class rule: "honest collector failure … never costs more than its own envelope's admission". The standard is whether a published number could be wrong. Model agreement is not evidence.

## Output

- For each question: a ruling, executed evidence, and a rationale.
- The final replacement text, as **amendment 35**, a self-contained text that S2's brief quotes verbatim. If you rule KEEP, write the sentence S2's brief carries instead.
- A 5-line plain summary for Ed. Ed is technical but has no project grounding, so use no internal ids without a gloss.

## Protocol

- A single non-interactive session: no background tasks, no subagents, every probe in the foreground. Edit no repository file other than the ruling file. Scratch files go under `/tmp`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-e6f06c96/docs/process_traces/2026-09-26-activation-e6f06c96/10-qpe-shape3/21-coldgate-fable-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 40 minutes. Mark any probe you could not run as NOT EXECUTED.
