# Charge — second addendum to cold gate A291-FIX2-01: rule the Astra cross-family refuter's objections to Final texts v2

Assembled 2026-09-24 ≈05:05 PDT by the resident magistrate (Opus 5.5, activation 278ebc9e). Nothing is armed.

## Background in plain words

A291 is the packer for scored measurement nights: `joulewise/scored_packer.py` builds a *roster* (which blocks of test items run in which measurement envelope, and what happens when an envelope overruns), seals it with a digest, and computes *derived* quantities from it (for example the spread shortfall lever). An independently written *checker* (`tests/scored_roster_checker.py`) must re-derive the same facts without copying the packer. Fix round 1 left three defects (a forged roster with two live placements accepted by the seal; a trusted-output cache letting a re-finalized roster skip replay; a derived value built from two different parent populations). Fix round 2 is planned as two seats: seat P rewrites the packer, seat K re-derives the checker and writes the generator, fuzz and stress modules.

History of the texts those seats will be briefed from, verbatim:
- `ex-10-coldgate-fable-ruling.md`: the cold Fable ruling on the fix-round-2 plan (Final texts 1–8).
- `ex-11-opus-contract-refuter.md`: the paired Opus 5.5 refuter on ruling 10 (1 BLOCKER, 8 MATERIAL).
- `ex-20-addendum-charge.md` and `ex-21-fable-addendum-ruling.md`: the cold Fable addendum; its §4 **Final texts v2** is the current one source for the briefs.
- `ex-40-astra-refuter-report.md`: NEW. Under D-184 (Ed, 2026-09-24: important science gets all four model families: Fable 5.1, Opus 5.5, Sol 6.0 and Astra 6) a cross-family Astra 6 refuter reviewed Final texts v2 at code `20cd29de`. It reports two MATERIAL findings (F1, F2), accepts texts 1–8 otherwise, and found all named regressions reachable. Its scratch probes are `ex-41-astra-*.py` (they expect to run with the repository at `20cd29de` on `PYTHONPATH`).
- `ex-02d-contract-v4.md`: the packer contract, version 4.

The magistrate reproduced F1's probe and F2's formatting probe at `20cd29de` (same tails as the report: baseline `ZeroDivisionError` on the zero-item parent; formatting-only copy ratio 12/236 = 0.050847 vs original 22/33). The magistrate takes no position on the cures.

## Questions (for each: AFFIRM Final texts v2 unchanged / ACCEPT Astra's replacement text / write a better text; give the final exact text)

- **B1 (Astra F1, MATERIAL).** "Gate ⇒ full indices" admits a zero-item parent (gate count 1, position count 0, relation true), so arithmetic divides by zero before full INV-10 runs at replay. Rule: a nonempty-`items` requirement in the pre-arithmetic INV-10 subset with refusal `inv_10`, the `_lever` precondition `0 < n_items == len(indices)`, and a new regression R4d; or another cure. Check whether the cure changes any existing regression's expected code (R2, R4b) or census property.
- **B2 (Astra F2, MATERIAL).** The line-similarity screen of Final text 8 is defeated by an AST-identical reformatting of the known transcription. Rule: canonicalise with `ast.parse` + `ast.unparse` before normalisation and add formatting-variant positive controls; or another method. State the threshold and the recalibrated controls you executed (Astra reports canonicalised copy 29/33 = 0.878788, control 8/33 = 0.242424).
- **B3.** Anything else these documents together expose that a seat would otherwise resolve silently.

Finish with one consolidated list, **"Final texts v3 (paste verbatim into the P and K briefs)"**, that supersedes Final texts v2 in full (restate unchanged texts in full so the briefs quote one place). Tier findings BLOCKER / MATERIAL / NIT.

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
2e438f596afd54cce1f277f962954d87ae66a17e8554d1127aeb59d683b3a728  ex-02d-contract-v4.md
d27455edf6aa73d583f8652f0dd64dbafaf17f0ce92b5cf5831597ece498986b  ex-10-coldgate-fable-ruling.md
db61a2da5275219d7034a8451c0710dd60da9a5fd81a782aaf8fa72e54430d1b  ex-11-opus-contract-refuter.md
a3140cf746edec25393565806ffc4d3c7282f1b90055418cf35d55860194fd0a  ex-20-addendum-charge.md
36a92bb2b8dc0f9213255ecd2fd508da87742bc9c1890683a283352fe99711a6  ex-21-fable-addendum-ruling.md
6124ab8a8d6f17818d5f386045276c275048407807d769afdbc6223fe37994a3  ex-40-astra-refuter-report.md
9a0206efbe2a596fae2cfdc046bc8d714e207af5457eb66b007fa9350001049f  ex-41-astra-probe.py
62079f8d5ba40da21f1aa8de5735030b744f3185bfe6b67c92f276ef923a9dfe  ex-41-astra-similarity.py
ece2b8559aa09c4e85c232d991a882ce04d7b8a569ef239971a780414971f52d  ex-41-astra-similarity_evasion.py
320785d45a686f6c6e77bb94e4230129c5c6b5a414663a8fec6157b8478a7a00  ex-41-astra-targeted.py
```
