# Charge — addendum to cold gate A291-ESC2-02: three narrow objections to Final texts A291-R4

Assembled 2026-09-24 ≈17:45 PDT by the resident magistrate (Opus 5.5, activation 278ebc9e). Nothing is armed.

## Background in plain words

Ruling `ex-20-r4-ruling.md` made the ownership harness the acceptance test for A291 round 3 and issued texts R4-0..R4-5. R4-0 is done: `ex-89-contract-v4-1.md` is contract v4 with only INV-11 replaced by the closed form.

The paired Astra refuter (`ex-86b-refuter.md`, probes `ex-86-probe-*` where present) executed R4-3 in a /tmp copy at `0fa4e6e3`. The legal corpus through the seal and all 71 existing tests PASS. It reports:
- **F1 BLOCKER, R4-5(3).** Mutation m3 (remove the terminal-item-in-holder clause) survives both mandated tests. The retained count clause already rejects a registered terminal item in any live holder, so m3 is an equivalent mutation on this corpus.
- **F2 should_fix, R4-3(4).** "In the same envelope" in the B1-singles-voided witness has two readings. Only the listing-local reading produces the required `superseded_live` witness.
- **F3 should_fix, R4-4.** P's exact read allowlist omits `joulewise/scored_packer.py` and `tests/test_scored_packer.py`, which R4-2 requires P to edit.

The magistrate takes no position. It notes one thing: the "impossible mutation kill" signature also appeared in R3 (ex-64b F4), and in R4 the judge ruled that "no equivalence claim is accepted for m1–m5".

## Questions

- **S1 (F1).** Rule m3: drop it as equivalent (with a proof on the corpus), supply a witness that kills it, or another text. Is any other mutant in m1–m5 equivalent? Execute.
- **S2 (F2).** Rule the reading.
- **S3 (F3).** Rule the read set.
- **S4.** Anything else.

Finish with **"Final texts A291-R4b"**, restating ONLY the changed R4 items in full; every other R4 item stands verbatim.

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`.
- Never touch `/Users/edr/code/JouleWise`, `/Users/edr/night-custody`, `/Users/edr/JouleWise-measurement-*` or `~/Library/LaunchAgents`.
- Code evidence comes from `git show 0fa4e6e3:<path>` and `git show 24ff94cb:<path>`, or from `/tmp` archive probes.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, memory, or `docs/process_traces` files outside this packet directory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
4a21353e3187339ffcf08cb2801dd43fe49e4eca7feea3fe94f01e85c4ca234d  ex-20-r4-ruling.md
b4682af2773e777da9b92d0dd61b6b89ebc0e10b5d195a4e81e78bd1ff5ae2ed  ex-86-probe-apply_predicate.py
450de0bb05a2d74a8cc62cb79c74068d51d848247cd67b671b8e784498182fbe  ex-86-probe-apply_r43.py
e7ff541243d3918bc40949a2b2bc1302a9f223498d6179474db0f11ca2d47035  ex-86-probe-control-packer.py
40e0cf40f33a6d3fd257ce4246e9a352bbb28d271890c2c862b8295bcc612710  ex-86-probe-m1-packer.py
3f848592af8556bae18b48dad6019762280155fc0e26a1a520068522e59f4a77  ex-86-probe-m2-packer.py
288e588c75591c499bc2637eb0c64c6fece0ccea6218383ce0064466028c2932  ex-86-probe-m3-packer.py
cf8c36bb462bd061c89fc901d8356c5cdf36adb026ee1d95be585b69cda900f3  ex-86-probe-m3-term-packer.py
9c896766a57bb88fe527dd53d81a4bb7a706eedebc905167e2149fcf19b40cfa  ex-86-probe-m4-packer.py
eb096d6a0cde4b0c9d7868e5d5c8cbcc287d944b4c33970fe0f962cc242025ee  ex-86-probe-m5-packer.py
aa2029f87351deabe95f9860cd6f899c94a7a9b444d9d1839a99729c5161e1b4  ex-86b-refuter.md
d88d10ddd8e4482988b740068306976ce093ce82fdb31498245985d3a603306d  ex-89-contract-v4-1.md
```
