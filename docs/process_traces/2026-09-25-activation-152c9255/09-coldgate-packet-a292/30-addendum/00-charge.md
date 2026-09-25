# Charge — cold addendum A292-REDUCER-DESIGN-01-ADD: rule the paired contract refuter's findings against the reducer ruling

Assembled 2026-09-25 ≈05:28 PDT by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed.

## Background in plain words

A cold Fable judge ruled the A292 reducer design (`ex-20-ruling.md`, on packet `ex-00-original-charge.md` and synthesis `ex-30-synthesis.md`). It found no BLOCKER; it amended S1, S3, S6, S9 and S13 and affirmed the rest.

A paired Opus contract-lens refuter, working independently on the same packet, reports 2 BLOCKERs plus MATERIAL and NIT findings (`ex-21-refuter.md`):
- **B1.** Refusing on a missing live window contradicts the gated obligation to re-run three A291 witnesses that omit a live key and assert a flag. Refusal is an amendment, not the no-new-rule option. Recapture does not exist until K25 is ratified.
- **B2.** A `stop_reason` vocabulary drawn from the runner module omits the normal end-token value `stop`, and "runtime failures are scored outcomes" invents a science rule.

You are the cold judge. The ruling and the refuter are both arguments before you, not authorities.

## Questions

- **E1.** For each refuter finding: AFFIRM the refuter's corrected text, write a different text, or REJECT. Give the deciding evidence from your own reading of the code (`joulewise/scored_packer.py`, `tests/test_scored_packer.py`, `tests/test_scored_packer_fuzz.py`, `joulewise/adapters/mlx_runtime.py`, `joulewise/scored_registration.py`) and of the rulings cited in ex-30's header. State where your ruling and the refuter conflict and which prevails. For B1, rule the missing-live-window policy on its merits: refuse (as an explicit amendment of the A291 re-run obligation), or a ruled typed outcome that the A291 surface already implies (not counted, cell flagged). Say which one keeps a counted number from being wrong and no item silently dropped.
- **E2.** Issue **"A292 reducer rulings v1.1 (final texts)"**: a complete, self-contained replacement for ex-20's final texts with every amendment folded in, executable by the harness and implementation seats without choosing. Include the exact schemas, the refusal codes with their triggers, the named tests, and both WRITE_SCOPEs. Add a plain summary of at most 5 lines for Ed.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl` or `powermetrics`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody`, `~/Library/LaunchAgents` or `/Users/edr/JouleWise-measurement-*`.
- Focused unit tests of named modules are allowed; the discovery suite is not.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory. Do not read any `docs/process_traces` file outside this packet directory and its parent, except the ruling files ex-30's header cites.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
99d9cbdd8e457f1a6ae9cebaa94e15d3dd79cd89019039972c5583f57d25e858  ex-00-original-charge.md
b6d49d96a6455cf0eadcf1ce3d5e49c44363f2baebeafa08e56414dd46963550  ex-20-ruling.md
316f770ba34ba02ba8e4e83c190e0b5b836fc2bcb8aa901d1f0188f2cbe7011b  ex-21-refuter.md
65f6656622a39b01628c23153e26f367e1853cca54c3dc253f9b84c5433f901d  ex-30-synthesis.md
```
