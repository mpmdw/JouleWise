# Cold gate CAP-COUNCIL-25G83-01-A2: rule on the cap plan after the owner's D-138 choice (a)

You are a COLD judge (Fable 5.1): a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first** (what you read that could bias you).

**Why this gate is mandatory.** The proposed decision amends a binding cold ruling (CAP-COUNCIL-25G83-01 addendum A1, step 1 and row S6) and decides how the claim hold H1 is enforced; both change the science plan, so a cold ruling is required. The owner's standing statement (2026-09-29): "all "gates" are meant solely to prevent death loops of useless investigation or reasoning and infinite tokenm burn, not to stop a component from being refined because we hit a fixec number of rounds, all rules are in service of the science". Where you set round limits, say what happens when one is reached (a consult, a cold gate, or the owner), not "stop for good".

**The packet** (directory `/Users/edr/code/JouleWise-wt-bk-ff50b201/docs/process_traces/2026-09-29-interactive-ff50b201/40-cap-a2/`; sha256 prefixes as trust anchors):
- `00-consult-charge.md` (018a471af230847e): the six questions and the background. Read first.
- `11-sol.md` (65482dcded5b2b8a) — Sol 6.1 seat; `12-astra.md` (4b1fed97dac13b92) — Astra seat; `13-opus.md` (8ea2b7404fc730bd) — Opus 5.5 seat. Independent answers; none read another's.
- The investigation that prompted the consult: `../30-r1-need/10-sonnet-r1-need-report.md`.
- The rulings being amended/applied, under `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/`: `20-cap-council/21-coldgate-fable-ruling.md`, `20-cap-council/31-addendum-ruling.md`, `12-hold-consult/21-coldgate-fable-ruling.md` (HOLD-BY-CONSTRUCTION-01), `12-hold-consult/40-owner-brief-2026-09-29.md` (the owner chose option (a)).
- Code: main `9eab16f8` (`git -C /Users/edr/code/JouleWise show origin/main:<path>`).

**The orchestrator's reading of the seats (check it; do not trust it):** all three agree on (1) a pin-only re-issue of R7 at 25F84 ("R8") as the default during the cap windows, preserving R7's 17 members (the charge's "same 12" was wrong), proven number-neutral by replay; (2) drop the interim 25G83 re-issue; (3) keep every 25G83 file unregistered until one closing transaction registers the successor and lifts H1 (no fourth hold design); (4) R8 via the existing re-issue tool, the successor via a generalized promotion tool in its own lane. Opus alone adds: R7's `derivation_notes` state the 165,000 cap as current fact and R8 must not copy them as such; A335 (OLD-EPOCH-EXPLICIT-R7-ROUTE-01) engages once R8 moves the default; the test option `--identity-epoch-json-for-test` can record a false build without the fake sampler (`scripts/validate_powermetrics_fiducial.py:2046-2060` on main) and must close before any claim window. Find where the seats disagree in detail (successor row handling, a third-window rule, what R8 must carry) — the orchestrator did not reconcile those.

**Rule on:**
1. The default during the cap windows: R8 or other; exactly what R8 must carry and what must be executed before it is admissible (replay, notes, A335).
2. The exact amended text of A1 §5 step 1 and row S6 (and any other step the new sequence changes; give the full re-sequenced step list if steps move).
3. The interim re-issue: drop or keep; what is recorded in its place.
4. How H1 is enforced from now until the closing transaction; whether the test-identity option must close first, and before what.
5. The tools: which produces R8, which the successor; lane boundaries.
6. Any point where a measured or published number could be false under the amended plan; name the check that prevents it.
7. The next three concrete actions, in order, and which of them need the owner (Ed approves new registrations and file names per the earlier cap ruling — say whether R8 is one).

**Protocol.** One non-interactive session, foreground only, no background tasks or subagents; ending before the ruling file exists is a protocol failure. Read-only: modify NO repository file except the ruling. Scratch: `/tmp/cg-capa2-ff50b201/`. Never read the battery; never run real `systemsetup`, `sntp` or `powermetrics`; never query the system log live. Budget: 60 minutes; anything not executed is marked NOT EXECUTED. Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-ff50b201/docs/process_traces/2026-09-29-interactive-ff50b201/40-cap-a2/21-coldgate-fable-ruling.md`. First line: `ADDENDUM: CAP-COUNCIL-25G83-01-A2 ISSUED`. Plain language, each term defined at first use. End with a 3-line plain summary.
