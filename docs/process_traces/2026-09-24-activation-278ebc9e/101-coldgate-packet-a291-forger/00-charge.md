# Charge — cold question A291-FORGER-01: the forger seat's model family (R4-5 item 4)

Assembled 2026-09-24 ≈19:52 PDT by the resident magistrate (Opus 5.5, activation 278ebc9e). Nothing is armed.

## Background in plain words

A291 round 3 is at `6e2504b1` (branch `fix/2026-09-24-a291-r3-packer`). The bench-verified status of the R4-5 gate:
- (1) the ownership harness is GREEN: 7 tests, 0 escapes in pairs and triples, named outcomes exact, legal corpus through the seal. The five scored modules pass 75 tests.
- (3) all five mutants are killed at the reference counts (`ex-100b-mutation-kills.md`).
- (2) the full discover suite is pending.

R4-5 item (4) (`ex-95-texts-r4b.md`) requires a **forger seat of a family "neither P's nor K's"**. P is Opus 5.5 (Claude family). K is Sol 6.0 (OpenAI/Codex family). The only other available models are Fable 5.1 (Claude family) and Astra 6 (OpenAI/Codex family, a different model from Sol). No third family is available. Read literally, the text cannot be satisfied.

## Question

- **T1.** Rule who the forger seat is. Options:
  - (a) Astra 6: same vendor family as K, but a different model, and never involved in P's code;
  - (b) a fresh Fable 5.1: same family as P, a different model, with no loop context;
  - (c) both, run independently, with the gate needing COMPLETED_NO_ESCAPE from both;
  - (d) another choice.
  Give the exact replacement text for the family clause of R4-5(4). Everything else in R4-5(4) stands.

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`.
- Never touch `/Users/edr/code/JouleWise`, `/Users/edr/night-custody`, `/Users/edr/JouleWise-measurement-*` or `~/Library/LaunchAgents`.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, memory, or `docs/process_traces` files outside this packet directory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
f48180cb4e3099bdc9e4f751b59c377f0a57d7c104f8da88b46b89d25a4e9e65  ex-100b-mutation-kills.md
14692d3ad6ef23c3e90785b24c58fb528e1af5903059227e4b2703d5edac8923  ex-85-texts-r4.md
63787c28d620c4811b327b85cf7d57db12eddf29aa40a0d17337ec87affd9b87  ex-95-texts-r4b.md
```
