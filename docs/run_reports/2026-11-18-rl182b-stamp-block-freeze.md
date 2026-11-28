# RL-182b stamp-block freeze, 2026-11-18

[AGENT], Tier 2. Draft PR #813 at parent `2fe705e73`. W1 base `b2e01464d`.
[RL-182b](https://github.com/mpmdw/JouleWise/blob/56f239dd25e09a39aed8cfdbea8028ebaefbab77/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21448)

RL-182b replaces the AST proof with a content hash and retains the tick test.
The new check reads the adapter as bytes and requires one exact start marker
line and one exact end marker line. It hashes from the start marker through the
byte before the end marker. The adjacent Pilot-10 check covers the remaining
source.

- Stamp block, 655 bytes over ten lines.
  `85ffe1a3cff318c6880d09d72b437c410a18f2dd92395ce62e08956d64c845c5`
- Whole adapter.
  `578455fa7b9ffb5582ef6c09ab5428d3078f3b1aea058409d39187de160a9336`

All 139 focused tests passed. The AST helper and both mutation tests were removed. The tick test body is
byte-identical to the parent and passes on all four existing synthetic paths.
The adapter, scorer, registration text and both state files are byte-identical
to the parent.

The independent executing-review check still requires entries for
`07ebee6c8` and `6093a7454`. The test-only scope leaves that gate for the
lead. Hosted CI and readback are recorded in PR #813.
