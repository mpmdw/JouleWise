# PR #813 audit round 6 repair, 2026-11-18

[AGENT], Tier 2. Audited head `6093a7454`. W1 base `b2e01464d`.
[RL-182a check 1](https://github.com/mpmdw/JouleWise/blob/45b2d57/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19946)

The original replay executed the chained assignment's prompt hash after the
prefill clock read on all four synthetic paths. Both ordinary spacing and
compact spacing passed the previous test with a gap of one tick.

Check 1 now constructs an allowed AST node for each discovered stamp write
and compares the whole statement to it. It accepts one plain name or dotted
attribute target, an optional plain annotation, and one direct
`self._clock.now()` call with no arguments. It checks the complete
assignment tree together with the existing adjacency and pair-count rules.

The exact-form regressions cover both chained-assignment spellings, a
walrus, a tuple target, a call argument, a lambda default parameter and an
expression wrapped around the token-0 read. Clean annotated and attribute
forms are accepted. The previous mutations still fail, and the clean
adapter still measures one tick for a cached first turn, a genuine cache
hit, an uncached turn and a suite item.

All 140 focused tests passed. An independent replay using the audit's in-memory compilation helper rejected
both chained-assignment spellings. The repair changes the check and its
tests. The production runtime, scorer and registration files match the
audited head byte for byte. Both state files are absent from the PR diff.

CI and final-head readback are tracked in draft PR #813. The independent
executing-review entries for the native-runtime commits `07ebee6c8` and
`6093a7454` remain the known CI gate.
