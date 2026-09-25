# Charge — cold gate A291-ESC2-02: after the text gate itself hit the escalation trigger, rule the METHOD and the round-3 plan, using the executed ownership harness as evidence

Assembled 2026-09-24 ≈17:10 PDT by the resident magistrate (Opus 5.5, activation 278ebc9e). Nothing is armed. This gate is MANDATORY for two reasons: round 3 would be a further fix round on the same defect, and the standing escalation trigger fired on the text gate.

## Background in plain words

The terms are built in `ex-47-synthesis.md`: seal, checker, ownership, and AUD-1.
- Cold ruling `ex-48-20-esc2-ruling.md` affirmed a structural cure and issued Final texts R3.
- The paired Astra refuter `ex-64b` found 4 BLOCKERs in R3.
- The cold addendum `ex-48-30-21-addendum-ruling.md` accepted all of them and issued R3b.
- The delta refuter `ex-71b` found 3 BLOCKERs in R3b and judged 7 of the 9 prior findings not cured: inv_51 has two owners in the boundary map; B1 cannot kill deletion of the superseded-holder clause; per-model formation accepts cross-model parent reordering.
- Every round has accepted the **closed INV-11 predicate** itself: it refuses the four forgeries and accepts 1,868 legal rosters.

Two consecutive text rounds failed on the same signature: texts meant for verbatim pasting carry implementation contradictions that only execution finds. So the magistrate ran no R3c. Instead it built, as TESTS ONLY and from the agreed content alone, an **ownership-forgery harness** (`ex-81-*.py`, report `ex-81b`, branch `test/2026-09-24-a291-ownership-harness` at `24ff94cb`):
- a closed INV-11 oracle written from the contract;
- composed ownership operators applied in pairs (exhaustive) and triples (sampled);
- a seal-level property: the oracle rejects ⇒ `_seal(finalize=True)` must refuse.
At the integration head `0fa4e6e3`:
- the oracle accepts the legal corpus and the legal contrast;
- the seal lets **109 of 4,800 pairwise and 105 of 8,092 sampled-triple forgeries** through, and accepts AUD-1, B1 and B2.
The magistrate takes no position on the method.

## Questions (AFFIRM / write a different ruling; exact final text; BLOCKER / MATERIAL / NIT)

- **N1 (method).** Is a round-3 brief that says "implement the ruled closed INV-11 and the `_ownership` view (ruling K1/K3); acceptance = the harness GREEN (zero seal escapes on pairs and sampled triples; legal corpus accepted) plus the existing 71 scored tests GREEN" sound? Or must the disputed boundary-map, AST and mutation-kill texts also be settled first? Say which R3b items stay binding, which are dropped, and which become harness-checked.
- **N2 (the three R3b blockers of ex-71b).** For each: rule it, drop it, or convert it into a harness case. For example, cross-model parent reordering becomes a generator operator.
- **N3 (the harness itself).** Is it an adequate acceptance test? Check it against the contract: missing operators, oracle clauses, the handling of inconclusive refresh and operator errors (239 + 642 recorded), and the triple sample size. Name the additions required before it is the gate.
- **N4 (seats and independence).** P implements the packer against the harness. The harness author must not be P. K's checker changes, if any, come from a different family than P. What P may read, and the order.
- **N5 (gate before merge and the stop rule).** Reuse ex-48-20 K5 (forger seat) as amended, or replace it with the harness.
- **N6.** Anything else.

Finish with **"Final texts A291-R4 (paste verbatim into the P brief)"**. Keep them short: this round's lesson is that long pasted texts carry contradictions, so prefer "the harness decides" wherever a test can decide.

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`.
- Never touch `/Users/edr/code/JouleWise`, `/Users/edr/night-custody`, `/Users/edr/JouleWise-measurement-*` or `~/Library/LaunchAgents`.
- Code evidence comes from `git show 0fa4e6e3:<path>` and `git show 24ff94cb:<path>`, or from `/tmp` archive probes. You may run the harness against a `/tmp` archive of `24ff94cb`.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, memory, or `docs/process_traces` files outside this packet directory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
2e438f596afd54cce1f277f962954d87ae66a17e8554d1127aeb59d683b3a728  ex-02d-contract-v4.md
e4bd4e94e9c6f342ad23f78ff0a0e2a6601ebabbbbf28820554218484c3b1701  ex-47-synthesis.md
32bdc18ed746d6b505458b9ffe76111b7656cdd32f5b8354901b88310c805540  ex-48-20-esc2-ruling.md
b359a6def3c4fce23c31fd3723cd0d0d7592c5d9238736b20a73e54de5c88427  ex-48-30-21-addendum-ruling.md
4128f37ce3ce2de7dcb9d6b21a24a30970096955c8bbc82db162fdb77099b059  ex-64b-r3-refuter.md
9f32f561546480fdec3c28abd4e60570b3a54e4e091b01048cd80d1da13dab6f  ex-71b-r3b-refuter.md
69ac40e04dbb7ecaeb7f3aee980b77c38037bdaa8da5bb3d8246776b1ae7b01d  ex-81-scored_ownership_generator.py
18d36054201046de361905c57cf4e36253848cafa557d73fd6b9b39c505ffb3d  ex-81-scored_ownership_oracle.py
dad26751c0059380d679d74947738048d745e3d4c87aff34c375f7403e0d46c2  ex-81-test_scored_ownership_forgery.py
55eeab814bce84bf7091fa05a959a04f527d45ab106bb9fa74de353d69bfc0a9  ex-81b-harness-report.md
```
