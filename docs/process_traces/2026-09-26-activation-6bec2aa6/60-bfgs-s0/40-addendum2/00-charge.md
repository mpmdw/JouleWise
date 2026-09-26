# Cold gate BFGS-DESIGN-01 — addendum 2 (S0 lens questions that need a ruling)

You are a COLD judge: a fresh session with no loop context. Your working tree is S0 candidate `26ab7234` (branch `feat/2026-09-26-bfgs-s0-helper-fence`). The packet files live on branch `docs/2026-09-26-8e43cfa7` at `b77677e9d4027637cedc28d3a06831a6b46d21fc` and are readable at the absolute paths below. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory/skill files.

**Authority.** Final texts v1.1 of the addendum ruling (you ruled a sibling of it): `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md` §4. Also the magistrate's bundle-span gap-fill: `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/60-bfgs-s0/20-ruling-bundle-span.md`.

**Lens reports on S0** (under `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/60-bfgs-s0/`):
- `33-opus-contract-lens.md`: B-1 and S-3 are the questions below.
- `31-sol-execution-lens.md` and `32-astra-execution-lens.md`: F1, the capture identity binding.

**Rule each question.** Give a decision, the exact text (numbered as amendments to v1.1), and reasons. Verify code claims by executed probes.
- **Q1 (Opus B-1).** The quiet-envelope span: its source fields, the seconds-to-nanoseconds conversion, and behaviour when `end_stamp` is absent. Particularly, the network-time-refusal envelope has `start_stamp`, zero rounds and no `end_stamp`, and text 5 puts both reads on that path. Opus recommends `start = floor(start_stamp.monotonic_before_s·1e9)` and `end = ceil(end_stamp.monotonic_after_s·1e9)`, or, for the exact refusal shape only, `end = ceil(start_stamp.monotonic_after_s·1e9)`. Any other absence would be `evidence_missing: quiet span unavailable`. Rule on this, on the clock-domain obligation on S2 (the same clock as `Clock.monotonic`, and the conversion rule), and on whether a malformed or reversed span is `evidence_missing` for every kind (Sol F2 / Astra R2).
- **Q2 (Opus S-3).**
  - Text 9 requires a `PairVerdict` of kind `bundle` "carrying `bundle_sha256`", but text 2's field list has no such field, and text 4 forbids constructing `PairVerdict` outside `battery_float.py`.
  - Text 12's `authenticate_window_members` lives in `battery_float.py`, which S1's WRITE_SCOPE excludes, and S4 comes after the epoch.
  - Choose between (a) S0 adds a `bundle_sha256: str | None` field, filled by `authenticate_bundle` from `complete_bundle_sha256`, and also adds `authenticate_window_members` as ruled in text 12; and (b) S1's scope gains `joulewise/battery_float.py` for exactly those two items. State the text-3 pin consequences either way.
- **Q3 (Sol F1 / Astra R4).** `authenticate_capture` takes its expected identity from the pre record itself. What must it bind to? Candidates: both attempt ids equal `instrument_evidence.validation_id`; pre and post agree on session, slot and attempt; and the ledger-owner binding, which may belong to the text-10 loader in S1. Say what S0 must do and what S1 must do.

**Protocol.**
- A single non-interactive session: no background tasks, no subagents, every probe in the foreground.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/60-bfgs-s0/40-addendum2/21-coldgate-fable-addendum2-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 40 minutes.
