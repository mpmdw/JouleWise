SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/whole_window.py", "joulewise/neg8_survivors.py", "tests/b5_analysis/test_validator_context.py", "tests/b5_analysis/test_neg8_parity.py", "tests/b5_analysis/test_neg8_predicate.py", "tests/b5_analysis/test_launch_lineage.py", "tests/b5_analysis/fixtures_s3.py", ".scratch-s3fix/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 90 minutes of wall time; write the report by minute 80 whatever is unfinished.** `tests.b5_analysis.test_validator_context` takes a few minutes with a warm fixture cache: run it in full twice at most.

# Fix round for stage S3 part A of lane L9 (the row validator): dispositioned review findings, two of them wrong admits

You work in the worktree and branch the launcher names (clean tree). An independent reviewer reproduced two
wrong admits and several weaker guards in `joulewise/whole_window.py` as changed by commit `e7ad34fde`. Read
`/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/REVIEW-s3a.md` (the
dispositions bind you; each "Fix" row states the rule to build) and the reviewer's probes under
`/Users/edr/night-archive/b5-consults/l9-rulings/s3/review-scratch/` (`probe_window.py`, `probe_answered.py`
and the mutated copies under `mutroot/` with `mutations2.out`: each is the counterfactual input for a row).
The first brief `BRIEF-sol-s3a.md` and the two rulings beside the review still bind you, the blinding
paragraph and the frozen-file constraints included; where a row of the review is narrower than a ruling's
letter, build the row (the lead has decided it, and it can only refuse more).

Build every row marked "Fix" that names this round (B1, B2, S1, the base-pin half of S2, S3, S4, N4). For
each: a test built from the reviewer's counterfactual input at the function concerned, going through the
real code path the reviewer used (for B1: real bundle bytes with the member's measured-window events
removed, not a stub), and a mutation run showing the test fails without the guard. The reviewer's surviving
mutants m1, m4, m5 and m7 must be killed by the final tests. Notes:

- **B2**: derive the closed list of NEG-8 condition names from what `scripts/run_campaign.py` and
  `joulewise/whole_window.py` can put into a NEG-8 bracket's or a row's conditions (read the code; list
  every site in your report), hold it as one named constant, and add a test that fails if the writer's
  source gains a `neg8_` condition word the constant lacks.
- **S2**: the neutrality tests' base is `git show b039c0257d1b1d407ee9598222db3f78f6ad7beb:joulewise/whole_window.py`;
  assert in the test that this blob's SHA-256 is the pin's (`configs/analysis/b5/seal_pins.json`), so the
  comparison can never be the file against itself. Scratch files go under `TMPDIR`, never the worktree. Do
  not touch how `fixtures_s3.py` builds windows: another seat replaces that with committed archives; a warm
  cache is in `.scratch-s3/windows` for now.
- **Without a context every function still behaves byte for byte as before** (ruling J1 item 12); show it
  again against the pinned base after your changes.
- Do not weaken any existing check; edit nothing outside WRITE_SCOPE. Part B's files
  (`joulewise/b5_analysis/context.py`, `sources_replay.py` and their tests) are another seat's: if your change
  alters a field or refusal that part B consumes, say exactly which.

Report: one line per row (guard location, test name, mutation output); the B2 site list; the neutrality
result against the pinned base; the final full result of the four S3 test modules.
