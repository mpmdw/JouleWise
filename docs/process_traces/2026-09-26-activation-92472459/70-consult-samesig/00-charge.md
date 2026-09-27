# Cold gate BFGS-SAMESIG-01: two same-signature recurrences (S2 authentication binding; S1 historical-set enumeration)

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory or skill files. **Write the contamination disclosure first.**

**Why you are convened.** The project's standing escalation rule: when two consecutive rounds fail with the same defect signature, the next spend is a consult, not a third round. Two lanes of one battery-gate change have each hit that rule. Nothing here has been adjudicated by the magistrate beyond what is stated.

## Part A: S2 (the quiet-night collector and summary), branch `feat/2026-09-26-bfgs-s2-qpe-collector`

Worktrees (read-only; do not modify): `/Users/edr/code/JouleWise-wt-s2lens-92472459` is detached @ `6c73caf4` (fix round 1). The current head is `a0e8e47f` = `6c73caf4` + one lead bench commit that reverts item F7 (`git -C /Users/edr/code/JouleWise-wt-bfgs-s2-92472459 show a0e8e47f`; that worktree is also read-only for you). Base `1417c0c4`.

- **Round 1** (Sol execution lens, `30-bfgs-s2/20-lenses/11-sol-execution-lens.md` finding B2): `pilot_summary` authenticated an envelope with `battery_float.authenticate_quiet_session(out)` and then re-read `session.json` for routing; a swap right after authentication changed the route.
- **Fix round 1, F4** (`30-bfgs-s2/30-fix1/10-fix-contract.txt`): read `session.json` and `rounds.jsonl` bytes before authentication (b0, j0) and after it (b1, j1); raise `CustodyFailure` if they differ; route only from b0/j0.
- **Delta 1** (Sol, `30-bfgs-s2/40-delta1/11-sol-execution-delta.md` B2 and S1): an A→B→A transition (passing bytes present only while the authenticator reads, the original non-passing bytes restored before return) passes F4 at both call sites, and a passing summary is written; probe `/tmp/bfgs_s2_aba_probe.py`. The journal comparison is unpinned (a mutant disabling it passes all tests). Opus (`40-delta1/12-opus-contract-delta.md` D-1, D-3) agrees on the unpinned journal check, finds F4 cannot raise on an honest night, and notes F4 reads before authenticating although amendment 32(2) says authentication runs "before the summary's own read".
- `joulewise/battery_float.py` (with `authenticate_quiet_session`) is frozen: its closure is pinned by merged tests and it is in no open WRITE_SCOPE.

**Q-A1.** Is the A→B→A case inside the threat the battery gate must close? The gate exists to stop a number measured while the laptop was charging from being published. State who or what could produce A→B→A on a real night (the collector, the executor, `record_attestation`, any other process) and what the probe needed to do it.
**Q-A2.** Rule the binding. Options include: (a) accept the residual, keep F4, pin the journal comparison, and record the reading of 32(2); (b) authenticate and route from one private snapshot: copy the envelope's files that the authenticator reads into a fresh temporary directory by bytes, call `authenticate_quiet_session(snapshot)`, and route from the snapshot's bytes, with no change to `battery_float.py`; state what the authenticator reads so the snapshot is complete, and its cost on a real envelope; (c) an amendment to the frozen helper so that it returns the bytes it authenticated; (d) other. Give the exact text, numbered as amendment 44 onward, and the test rows (production call sites `pilot_summary` and `summarize`), including the counterfactual each must die under.
**Q-A3.** The lead reverted F7 at the bench (`a0e8e47f`): the refusal path writes `session.json` then `rounds.jsonl`, as before S2, because a journal-first order turned an honest interrupted write into a custody failure (Sol delta B1, reproduced by the Opus delta D-2). Uphold or reject the revert.

## Part B: S1 (the bundle reader's historical set), branch `feat/2026-09-26-bfgs-s1-bundles`

Worktree (read-only): `/Users/edr/code/JouleWise-wt-s1cg-92472459`, detached @ `b859317c` (the fix round implementing amendments 36–43 of the BFGS-S1-SCOPE-01 erratum ruling, `20-bfgs-s1/40-coldgate/30-erratum/21-coldgate-fable-erratum-ruling.md` §4). A round-2 seat is editing a different worktree concurrently; do not use it.

- **Round 1**: the historical set was built from test fixtures only and missed 50 real bundles named by a committed detection-floor file (C-2 of the BFGS-S1-SCOPE-01 ruling).
- **Fix round**: amendment 40's content enumeration; the set is now 69 entries (13 fixtures + 50 floor + 6 RPT001 tree digests), and both delta lenses verified the 69 exact.
- **Delta 1** (Sol, `20-bfgs-s1/55-delta1/11-sol-execution-delta.md`): F2, the text scanner accepts only two literal keys on ordinary lines, so `bundle_tree_sha256: aaaa…` in a text file yields no candidate (probe `/tmp/bfgs_text_candidate_probe.py`); no current entry is missing. F1, the reverse witness report exits zero on a byte-modified copy of a historical bundle, because it checks a named entry only after a digest hit (probe `/tmp/bfgs_reverse_probe.py`); the reader itself refuses the modified copy. Opus (`55-delta1/12-opus-contract-delta.md`) SF-1 to SF-3: an identity test masked by duplicate rejection; no row for a digest-matching `config.json` failing re-validation; duplicate RPT001 labels depend on file order.

**Q-B1.** Is F2 a sign that enumeration by text scanning is structurally unsound, so that the builder should instead enumerate from a closed, declared list of citation sources and fail on any unclassified digest-shaped key, or is a pattern fix sufficient? Rule the exact text (amendment 44 onward; do not reuse Part A's numbers).
**Q-B2.** Rule the witness's semantics: must it flag an encountered bundle whose run id or path names a set entry but whose digest misses?
**Q-B3.** Confirm that Opus SF-1 to SF-3 and Sol F3–F5 are test/label fixes for S1's next fix round with no text change, or rule otherwise.

**Packet root** (absolute): `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/`. The ruled texts both lanes implement are listed in `30-bfgs-s2/10-seat-brief.txt` (S2) and `20-bfgs-s1/50-fix1/10-fix-brief.txt` (S1).

**Keep intact:** custody is never a status; authentication precedes every exclusion decision; `joulewise/battery_float.py` byte-identical unless you rule option (c) as a numbered amendment with its pin consequences.

**Output.** Per question: ruling, executed evidence (re-run the probes you rely on; mark anything not run as NOT EXECUTED), exact text. End with a 5-line plain summary for Ed (technical, no project grounding; gloss every internal id).

**Protocol.** A single non-interactive session: no background tasks, no subagents, every probe in the foreground. Edit no repository file. Scratch under `/tmp`. Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/70-consult-samesig/21-coldgate-fable-ruling.md`; ending before that file exists is a protocol failure. Budget: 50 minutes.
