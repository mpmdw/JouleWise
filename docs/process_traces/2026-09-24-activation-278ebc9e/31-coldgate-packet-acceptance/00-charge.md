# Charge — cold gate ACCEPTANCE-25G83-01: rule the D-184 council's synthesis on instrument acceptance on macOS 25G83

Assembled 2026-09-24 ≈06:10 PDT by the resident magistrate (Opus 5.5, activation 278ebc9e). Nothing is armed.

## Background in plain words

Every science measurement night on this machine needs a D-079 calibration acceptance, bound to the live operating-system build. The active acceptance, r7, is for macOS 25F84. The machine runs 25G83. On 25G83 `powermetrics` delivers samples about every 0.245 s at a requested 100 ms, where r6 saw about 0.120 s. On 09-19 two one-night checks produced 13 invalid captures out of 24. Ed then chose option (c) (`ex-ed-ruling-20260919-c.md`): resolve the instrument first, and "make sure the barriers to acceptance aren't overly strict for no reason".

A Sol scout assembled the facts (`ex-22-packet-*`). Four blind seats answered: Sol (`ex-24`), Astra (`ex-25`), Opus (`ex-26`) and Fable (`ex-27`). The magistrate's synthesis and proposed rulings R-ACC-1..6 are in `ex-30-acceptance-council-synthesis.md`; its opening section builds the terms (acceptance, capture, fiducial detector, B, corpus). You are the cold judge. The seats and the synthesis are arguments before you, not authorities.

Ed's standard, verbatim: the orchestration exists for "preventing bad science, not progress on the paper when models agree". The D-184 addendum (Ed, 2026-09-24) lifts the major-decision hold: the four-model council decides experiment design, Ed is informed after, and Ed is owner-only for hardware, sudo, a notice NO and claim publication.

## Questions (for each: AFFIRM / write a different ruling; give the final text; tier concerns BLOCKER / MATERIAL / NIT)

- **H1 (R-ACC-1).** Protocol v4: pulse length (1.5 s vs 2.0 s), the authenticated window, and the replay precondition. Verify the interior arithmetic against `joulewise/powermetrics_fiducial.py` and the observed interval distribution.
- **H2 (R-ACC-2).** Registration rev 2: the number of windows, their spacing, retained n (10 / 12 / 19), the futility stop, blindness, the disclosure of seen data, and the simulation precondition. Say which barrier has a physical reason and which does not, and whether n ≥ 12 is defensible for the bounds the acceptance issues. Check the pre-registration `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` for anything the change would silently break.
- **H3 (R-ACC-3).** A243 attribution as a parallel diagnostic, not a gate.
- **H4 (R-ACC-4).** Authority. Does anything in the pre-registration (for example `:11-13`) or the decision log require Ed's written acknowledgement for a revision, notwithstanding the D-184 addendum? If it does, state exactly what Ed must acknowledge, in one line.
- **H5 (R-ACC-5, R-ACC-6).** The macOS auto-update hold and the order of steps.
- **H6.** Anything the synthesis dropped or merged wrongly. Check at least the seats' B-value and yield claims against the packet.

Finish with **"Acceptance rulings (final texts)"**: one numbered paragraph per ruling, executable without choosing, and a plain-language summary of at most 10 lines for Ed.

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody` (reading archived records is allowed), any `/Users/edr/JouleWise-measurement-*` directory, or `~/Library/LaunchAgents`.
- Repository evidence may be read in your worktree.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports, memory, or any `docs/process_traces` file outside this packet directory, except the 2026-09-19 records that the exhibits cite.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
8031566bb7cce1c1110b53dbda6e1c33aa069de9d5f022e448a676cf5f6b4d3d  ex-22-packet-00-question.md
20c28acd123129b2ebe3ed6b1a8dee46c29db9507f93e444c14273cf434db6fe  ex-22-packet-01-cadence-facts.md
ac880d9f0102b742af9cd2fd021e19c4d39288f788a2912726d2bfcac23c1b39  ex-22-packet-02-acceptance-rules.md
4c46561271c0665187b13d4c620abc82330bb0e21434e9f68fa6c05ecbac6532  ex-22-packet-03-evidence-inventory.md
94bc7eba81b31ebc5cbde1983cfe73be24f61f5b7e04e76b5e8737505e9ece30  ex-22-packet-04-options.md
e64d16bd1cfe6694a61beac7715839fc3285df98cf6b1f9d4343a0d2443f9046  ex-22-packet-05-open-facts.md
1d45297492d9658c0c675dd811af3eee5274562653f17f693290f6a3f92b1628  ex-24-acceptance-seat-sol.md
02a83d255e2e52ca9773faa10981210df3e18f78188006605cbecdf427fb718b  ex-25-acceptance-seat-astra.md
d6929497af62a4af96523c97e8a7fd943bc4594aa4e1948b4b7a5bc3858a8880  ex-26-acceptance-seat-opus.md
abd4df2d624ea6d3acb08b5730fe3d7795708ccf035aec8e68906e030e8e64f7  ex-27-acceptance-seat-fable.md
373143cc82ee0d1d6dc3f585fa340dccb9f47dc24c88efb50d1f2c4c87ac63a7  ex-30-acceptance-council-synthesis.md
d0d36a0c0abe06e8b448eb09b5447fcc3ce8693e5ad4597b7e4ccb6ce8b0cddb  ex-ed-ruling-20260919-c.md
```
