# Charge — addendum to cold gate A291-FIX2-01: rule the paired refuter's objections to the ruling's Final texts

Assembled 2026-09-24 by the resident magistrate (Opus 5.5, activation 7370d0fb). Nothing is armed. In round 1 of this gate:
- the charge is `ex-00-charge.md`;
- the cold Fable judge's ruling is `ex-10-coldgate-fable-ruling.md`;
- the paired cold Opus contract refuter, `ex-11-opus-contract-refuter.md`, attacked the ruling's Final texts 1–8 as two implementation seats would have to build them. It reports 1 BLOCKER, 8 MATERIAL and 5 NIT, with executed evidence X1–X9.

The refuter AGREES with Final texts 1 and 5, with B2's residual, with B7 and with the B5 order. The magistrate takes no position on any item. This addendum decides the text that seat P (packer) and seat K (checker) will be briefed from, verbatim. Every cure must be exact and must leave the seat no choice.

## Terms in plain words

The terms are as built in `ex-00-charge.md` §"Terms in plain words", and in `ex-06-plan.md` §1.
- *Seat P* rewrites `joulewise/scored_packer.py` and its tests.
- *Seat K* re-derives the independent checker and writes the case generator, the stress module and the mutation-fuzz module.
- To *reseal* a roster is to recompute its digest on the test side using the checker's `digest`.

## Questions (for each: AFFIRM the ruling's text / ACCEPT the refuter's replacement / write a better text; give the final exact text)

- **A1 (F1, BLOCKER).** R2b cannot raise `inv_12` as written (X2). Rule the replacement: the flip-`superseded` mutant (X3), or another.
- **A2 (F2).** INV-11 has two readings: the 02d:468 predicate, and 45/21 §7(S). Rule which one packer and checker implement, and the residual.
- **A3 (F3).** The exact handler list and order in `_checked_derived` and in `_seal`'s try block.
- **A4 (F4).** Is executed arithmetic brought inside the boundary, and does fuzz property (a) extend to `executed_status`?
- **A5 (F5).** Signatures and record shape of `_parent_facts` and `_lever`; R4b's patch value.
- **A6 (F6).** Renaming `_live` to `_live_index`, and the R4c AST text.
- **A7 (F7).** Fuzz properties (c) and (e), mutation bases, and the extents of operators (5) and (9).
- **A8 (F8).** Protecting P's E1–E11 gate witnesses and imports from K's rewrite; the refuter offers two options and says the magistrate picks the first. Rule it.
- **A9 (F9).** The similarity-check method and its threshold.
- **A10 (F10–F14, NITs).** R1 wording, R5b, INV-10 extent, the X-5 citation, and naming the five modules.
- **A11.** Anything else the two documents together expose that a seat would otherwise resolve silently.

Finish with a single consolidated list, **"Final texts v2 (paste verbatim into the P and K briefs)"**, that supersedes ruling 10's Final texts, so the briefs quote one place. Tier findings BLOCKER / MATERIAL / NIT.

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody`, any `/Users/edr/JouleWise-measurement-*` directory, or `~/Library/LaunchAgents`.
- Code evidence comes from `git show 20cd29de:<path>`, or from probes in a `git archive 20cd29de` copy under `/tmp`.
- Write only the ruling file.
- Do not read any `docs/process_traces` file outside this packet directory, or RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
8e99b258e476274737842f4bb8c178b4be438c79392da4139800b1bf986d99bb  ex-00-charge.md
2e438f596afd54cce1f277f962954d87ae66a17e8554d1127aeb59d683b3a728  ex-02d-contract-v4.md
2ecfea12bd15527e8c820272a3b583329692e0eabe97f52cb5d8bb127e5042eb  ex-06-plan.md
d27455edf6aa73d583f8652f0dd64dbafaf17f0ce92b5cf5831597ece498986b  ex-10-coldgate-fable-ruling.md
db61a2da5275219d7034a8451c0710dd60da9a5fd81a782aaf8fa72e54430d1b  ex-11-opus-contract-refuter.md
37f5064b95cabe5752d4564343b93dfa4c42b66041a1afe84e225dfade7446a6  ex-31-residual-rulings.md
```
