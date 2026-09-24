# 37 — A281a STOPPED under its lane stop rule; consult brief (for blind Sol and Opus seats)

## Stop record (magistrate)

The fix round 2 head is `c0998fdb`. Both delta lenses FAIL with CLASS-IV (silent-default / guard-skipped-on-a-path) findings, and they are four distinct instances:
- Opus 39 B1: the registered `item_set_sha256` is never compared; `pack` accepts any item set under one registration digest.
- Opus 39 B2: the M12 worst-case guard compares against a caller-supplied `failed_prediction_s`, never the roster's own `predicted_s` / `predicted_item_s`; `pack` accepts predictions above the registered ceiling.
- Sol 34 B1: the retry append path packs two blocks of one cell into one envelope (M8's one-block-per-cell-per-envelope guard is skipped on that path), and the roster stays `claim_ready`.
- Sol 34 B2: `min_blocks_per_cell` and `min_envelopes_per_cell` accept 1, so the M8 five-block spread becomes a registration value.

Brief 26 §STOP RULE (refuter R12): a class-iv finding in the round-2 delta stops A281a and convenes a consult; there is no round 3. This is also the standing escalation trigger (same signature, consecutive rounds). Any round 3 is a third fix round on the same defect class, so a cold gate must rule on it before it runs. The other findings (Opus 39 S1-S7, N1-N6; Sol 34 S1) travel with whatever round the gate allows.

## Consult brief

ROLE: blind design-consult seat for JouleWise lane A281a (Registration + scored packer + scored reducer, pure stdlib modules at head c0998fdb in /Users/edr/code/wt-d8cc9c0a-pure-review). ESCALATION consult: class-iv defects (a registered input or guard that is missing, defaulted, caller-overridable, or skipped on some code path) have now appeared in three consecutive review rounds, even after a round whose whole purpose was a structural cure (a frozen, no-default Registration object plus no-default and drop-key sweeps). You have licence to disagree with everyone. Read-only; scratch only under /tmp; named modules only (`python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer tests.test_scored_reduce`); never import or execute from /Users/edr/code/JouleWise; never touch /Users/edr/night-custody.

Records (directory /Users/edr/code/wt-d8cc9c0a-bk/docs/process_traces/2026-09-23-activation-d8cc9c0a/): 26 (fix brief G1-G6), 27 (report), 34 (Sol delta), 39 (Opus delta), 21-coldgate-packet-a281/10 and /11 (cold gate ruling and refuter), 20 §Q4 (field list).

Questions:
- Q1 Why did the no-default Registration not close class iv? The magistrate's hypothesis, to test and not assume: the sweeps check that a field is PRESENT, never that it is CONSUMED. A registered value can be present, validated and then ignored (item_set_sha256), or bypassed by a caller argument (failed_prediction_s), or enforced on one path but not another (M8 on the initial pack, not on retry tails), or registrable to a value the design forbids (min_blocks = 1).
- Q2 Propose an acceptance shape that makes class iv enumerable, so a reviewer's fresh reading cannot find a new instance. For example: a binding matrix with one row per registration field and per ruled invariant (M7, M8, M12, the drift rule, the cap rule). Each row names every consuming code path (pack, each requeue stage, reduce) and a test that a violating input refuses ON EACH PATH. The matrix goes in the brief, and a test asserts that every Registration field appears in it. Is that sound? What is its failure mode? Give the matrix for the current modules.
- Q3 Which ruled values should be constants rather than registration fields (min_blocks_per_cell = 5, min_envelopes_per_cell = 5, cap_bound_fraction, …)? Which caller arguments should disappear (failed_prediction_s at the block stages; items_by_level versus the registered item ids)?
- Q4 The M12 amendment (several singles per envelope) versus M8 (one block of a cell per envelope): which rule wins on retry tails, and why? Is either ruling wrong?
- Q5 Should A281a continue at all in this shape, or be re-cut (for example registration + packer first, reducer after)?

Output: a report answering Q1-Q5, under about 1,800 words, with the Q2 matrix as a table.
