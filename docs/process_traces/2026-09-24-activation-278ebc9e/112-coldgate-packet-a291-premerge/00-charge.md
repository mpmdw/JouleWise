# Charge — cold question A291-PREMERGE-01: which post-review changes land before the final pass on the A291 merge candidate

Assembled 2026-09-24 ≈21:10 PDT by the resident magistrate (Opus 5.5, activation 278ebc9e). Nothing is armed.

## Background in plain words

A291 round 3 (the packer's ownership view) has passed the gate items of rulings R4/R4b and FORGER-01/02:
- the harness is GREEN (bench, 10 tests at `3fb98469`);
- the five scored modules pass (75 tests);
- the mutation kills m1–m5 all kill (`ex-100b`);
- both forgers reached COMPLETED_NO_ESCAPE: F-C and F-B each had nine OUT_OF_ROUND candidates, all refused by replay (`ex-104`, `ex-106`);
- entry-path witnesses exist for INV-23/36/37 (`ex-107b`, `ex-108b`).
The full suite is running.

The merge candidate is `fix/2026-09-24-a291-merge-candidate`: main plus the lane, 12 files, +4,223 lines. Post-review findings:
- **Astra contract lens (`ex-110a`):** a nit. `_ownership` lacks the ruled `-> dict` annotation.
- **Sol execution lens (`ex-110b`):** should_fix. A `sha256` field of 1,200 nested lists raises `RecursionError` from `_seal` and `requeue_overrun` instead of `PackingRefusal`. The magistrate's probe (`ex-110c`) shows this is pre-existing, identical at round-2 head `0fa4e6e3`. The cure would be one line: `RecursionError` added to `_seal`'s conversion tuple.
- **Opus counter-review (`ex-111b`):**
  - R6-1, level/night confound in `pack`: should_fix, a blocker for the first registered night, not for the merge;
  - R6-2, a runner obligation, plus an optional index cut;
  - R6-3, a nit;
  - CI cost, should_fix: no timings entries for six new test modules;
  - it recommends the RecursionError fix alongside the merge.

R4-2 says "nothing else in the module changes", so the magistrate has made no bench change.

## Questions

- **V1.** For each of these, rule: before the final pass (on this branch, then a fresh-eyes review of the post-review commit), or a follow-up lane:
  - (a) the `-> dict` nit;
  - (b) `RecursionError` in the conversion tuple, plus a regression test;
  - (c) `scripts/test_timings.json` entries, with the forgery and stress modules marked exclusive or split;
  - (d) the R6-2 index cut.
  Give exact texts for anything that lands now.
- **V2.** R6-1: confirm that it gates the first REGISTERED night and not this merge, and name where it is decided. The magistrate's plan: it joins the headline redesign work (AP-5M v5 and the A291 contract v5) and its council and cold gate.
- **V3.** The final-pass packet: list exactly what it must contain (gate items and pins) so the next Fable pass can rule MERGE / NO-MERGE on an exact sha.

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`.
- Never touch `/Users/edr/code/JouleWise`, `/Users/edr/night-custody`, `/Users/edr/JouleWise-measurement-*` or `~/Library/LaunchAgents`.
- Code evidence comes from `git show <rev>:<path>` for `3fb98469`, `e3769062` or `0fa4e6e3`.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, memory, or `docs/process_traces` files outside this packet directory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
f48180cb4e3099bdc9e4f751b59c377f0a57d7c104f8da88b46b89d25a4e9e65  ex-100b-a291-mutation-kills-report.md
74f939a525f502f1b24286e3e4e150c116d9dff6f9a6240045cfd24a66a0d9aa  ex-104-fc-adjudication.jsonl
2ba12cf54dbad0c8e726ace48c806a172200aa33ee7a7b808cce804f18029953  ex-106-fb-adjudication.jsonl
caddf2b5b44b25d50c8daaaf5a147a970c7be36b17a5cd80ab482a0bf49e2676  ex-107b-a291-typed-code-line.md
c22c568c90ca02c94d1dfa600cbad60d214dc899817630bee025a30629878b1e  ex-108b-a291-entry-witness-report.md
7a5de37f1c3dd121a6b169eaa636907c0b4a617c89aeb1e00002df4a1c46b051  ex-110a-a291-r3-contract-lens-astra.md
81551579b7804c13d931e5c581429bcf3d5a66a4e4621f3b6ec678e4a0aeca6e  ex-110b-a291-r3-execution-lens-sol.md
6351aafb7ea9c2470063e4e97a118ac68b310dd2217b1f9f30c553daac03f098  ex-110c-recursion-probe.py
7717e5485a8d70e1ec556bf06c41794e3e5281b13efb57c80b0861ef5044d2c6  ex-111b-a291-opus-counter-review.md
63787c28d620c4811b327b85cf7d57db12eddf29aa40a0d17337ec87affd9b87  ex-95-a291-final-texts-r4b.md
```
