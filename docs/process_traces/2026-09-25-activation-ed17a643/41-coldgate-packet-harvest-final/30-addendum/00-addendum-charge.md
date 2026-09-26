# Charge: cold addendum HARVEST-VERDICT-FINAL-01-ADD. Rule the paired refuter's findings and issue final obligations v1.1.

Assembled 2026-09-25 ≈18:00 PDT by the resident magistrate (Opus 5.5, activation ed17a643). Nothing is armed.

## Inputs (in this packet directory, `..`)

- `00-charge.md` and its exhibits: the original charge.
- `20-coldgate-fable-harvest-final-ruling.md`: the cold Fable ruling (a committed per-window verdict file; the issuer refuses on disagreement; A-R5b-1 text; obligations 1–11).
- `21-opus-contract-refuter.md`: the paired Opus refuter. Phase 1 is independent. Phase 2 raises one BLOCKER, that §4.2's HEAD-only authentication lets an ordinary `git rm` and re-commit re-record a verdict after B is seen (P2-E1), and four MATERIALs: (a) a custody clause for the pre-record and regenerate-before-commit window; (b) the last window of an epoch has no external anchor; (c) two sentences for A-R5b-1; (d) exemption (i) rests on an unpinned disposition registry. Its Phase 1 also carries R4 (the registry route drops a clean window; pre-existing) and R5 (`battery_float.py` code drift after harvest).

These are arguments, not authorities. You are a fresh instance.

## Questions

- **Y1.** Verify each Phase 2 finding and R4/R5 yourself at `origin/feat/2026-09-25-bfg-d` (`ab431280`; the only change after the ruling's `06671b69` is the N-1 liveness constant) with executed evidence. For each, AFFIRM, AMEND or REJECT. Say in particular whether the custody clause ("a completed, ledger-authenticated probe whose raw bytes are absent or mismatched is a custody failure, never `evidence_missing`") is an admissible reading of A-R5b "Window verdict" without a text change.
- **Y2.** Issue **"Harvest-verdict final obligations v1.1"**. It must be complete and self-contained, superseding the ruling's §4.2, §4.4's residual, §4.5 and §6. Include: the exact authentication checks; the exact final A-R5b-1 decision-log text; the registry pin; the anchor timing; the full numbered implementation-obligation list with tests; and a corrected plain summary for Ed of at most 5 lines. An implementer must be able to execute it without choosing and without reading the ruling or the refuter.

## Constraints

- Work as one non-interactive foreground session. Start no background tasks, watchers or subagents. Ending before the ruling file exists is a protocol failure. Budget about 25 minutes.
- Read-only. Never run `sudo`, `launchctl`, `powermetrics`, the installer or model inference. Never touch `/Users/edr/code/JouleWise`, `/Users/edr/night-custody` or `~/Library/LaunchAgents`. Focused unit tests are allowed; discovery is not. A detached scratch worktree under `/tmp` is allowed; remove it afterwards.
- Write only `30-addendum/21-coldgate-fable-harvest-final-addendum-ruling.md`.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory, or any `docs/process_traces` file outside this packet except `../10-coldgate-packet-bfg/`.
- Begin with a contamination disclosure.

Charter: `docs/process/coldgate_charter.md` sha256 `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`.

## Input manifest
```
3f3e9c0f7745884ac30c71682c4d97676f0769ea67d8fa21e7380650d298bb2f  20-coldgate-fable-harvest-final-ruling.md
633a84ec06e98f3756727d37cc130a6b4b5d6ee839ec1b1d5826d7e673d56e2e  21-opus-contract-refuter.md
d0cbd53ef6820c4eecb9115be278d72e733ac61e4a09e9283504db2f6fad4ea5  00-charge.md
```
