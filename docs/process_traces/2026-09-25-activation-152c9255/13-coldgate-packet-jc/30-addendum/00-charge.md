# Charge — cold addendum JCORRECT-FLOOR-01-ADD: reconcile the paired statistics refuter with the J/correct ruling

Assembled 2026-09-25 ≈06:35 PDT by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed.

## Background in plain words

A cold Fable judge ruled the J/correct floor council (`ex-20-ruling.md`, on packet `ex-00-original-charge.md` and synthesis `ex-30-synthesis.md`):
- it verified the claim-gate BLOCKER, that the ruled CG-1 omits the shared accuracy sampling error, with 25–89 % false admission per level;
- it replaced the magistrate's P-0 with amendment A-JC-1, which uses a Welch df rule;
- it affirmed option (c) with a directly matched two-model null and 14 null windows.

A paired Opus contract/statistics refuter, working independently on the same packet (`ex-21-refuter.md`), affirms the BLOCKER (0.84 false admission per level on the instrument-only premise) and the Welch df, and raises MATERIAL findings:
- **P0-b:** V_env counted twice if the draft's cluster bootstrap supplies V_acc;
- **P0-c:** the claim's population is unstated. For "this frozen set" under seeded decoding V_acc = 0, while for the level population V_acc > 0 and needs stratification;
- **P0-d:** Δ_L has no envelope form. The rules for what k counts, how the 8B and 1.7B envelopes pair, and the estimator are all undefined;
- **P0-e:** the B conversion and the sign-flip test;
- **C-1:** a contradiction with WR-1;
- **C-2:** the 10 % byte-identity ceiling versus WR-1's exclusion;
- **S2:** the floor transfer is not shown to be conservative;
- **power** at the planned n_acc.

You are the cold judge. The ruling and the refuter are both arguments before you, not authorities.

## Questions

- **H1.** For each refuter finding, say whether ex-20 already resolves it (cite the text), or AFFIRM the refuter's corrected text, or write a different text, or REJECT. Give your own desk simulation where the finding is statistical. P0-c is a science-meaning choice. Rule it outright if the ruled texts and AP-5M v5 fix the population. Otherwise name it as the single question the four-model council must answer, with the two options and their consequences.
- **H2.** Issue **"J/correct floor rulings v1.1 (final texts)"**: a complete, self-contained replacement for ex-20's final texts with every amendment folded in, executable without choosing. It must include the CG-1 amendment text (SE, df, V_acc estimator, population, envelope form, pairing, the estimator), and the simulation acceptance criterion with its power statement at the planned n_acc. Add a plain summary of at most 8 lines for Ed.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl`, `powermetrics` or model inference.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody`, `~/Library/LaunchAgents` or `/Users/edr/JouleWise-measurement-*`.
- Desk Python and focused tests are allowed; the discovery suite is not.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory. Do not read any `docs/process_traces` file outside this packet directory and its parent, except the files ex-30's header cites.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
64c97214dc175f281d098e580cc91dbcb4d259536153680e28b155d5710dfc0f  ex-00-original-charge.md
a33bde5b2fa0cf2ab9be77778011910f4633bb6121723eaf4b5cb761bdf54caf  ex-20-ruling.md
bce22f681e25a8eade031300be8a73425e57f502727412de70c713853143ea35  ex-21-refuter.md
bcb9422c31b28c2a31b54b57ac6848f4503b3339a10fe4ef934b8b598658e580  ex-30-synthesis.md
```
