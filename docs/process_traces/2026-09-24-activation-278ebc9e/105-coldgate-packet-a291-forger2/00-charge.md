# Charge — cold question A291-FORGER-02: F-A escalated after two INCONCLUSIVE runs; disposition of F-C's nine OUT_OF_ROUND candidates

Assembled 2026-09-24 ≈20:10 PDT by the resident magistrate (Opus 5.5, activation 278ebc9e). Nothing is armed.

## Background in plain words

Ruling `ex-101-forger-ruling.md` requires two independent forger seats: F-A (Astra 6) and F-C (a fresh Fable 5.1). Item (4) of the round-3 gate passes only when both reach COMPLETED_NO_ESCAPE. One INCONCLUSIVE reruns once; a second escalates.

- **F-A:** both runs were INCONCLUSIVE (`ex-103-fa-runs-summary.txt`, `ex-103b-fa-run2.md`). OpenAI's service refused the task as a possible cybersecurity risk. Run 2 used brief `ex-102a` (validator-robustness wording, "invalid" for "forged"), and the filter fired again. So F-A has escalated.
- **F-C:** reached COMPLETED_NO_ESCAPE under the ruled definitions (`ex-104-fc-report.md`; adjudication `ex-104-fc-adjudication.jsonl` produced by `ex-104-adjudicate.py` with the ruled oracle and checker at `6e2504b1`).
  - The seal accepted nine hand-built rosters. On every one, the oracle reports nothing and the checker reports only INV-23/36/37/38/52 (event replay, attempt history, terminal provenance, types), never INV-10 or INV-11. So all nine are OUT_OF_ROUND.
  - F-C's own diagnosis: the closed INV-11 is tight. The seal does not bind placements and voidings to events, does not check a terminal refusal's other fields, does not check that single-of-single parents came from pack, and skips the digest chain under finalize. Replay catches the cases re-checked (`inv_38`).

The other round-3 gate items stand as follows. (1) The harness is GREEN (bench). (3) All five mutants are killed. (2) The full suite is running.

## Questions

- **U1.** Who replaces F-A, or is item (4) satisfied by F-C alone given the vendor refusal? Options:
  - Sol 6.0 (the same vendor as K and a different model; likely filtered too);
  - a second independent fresh Fable 5.1 with no shared context;
  - F-C alone, recording the vendor refusal;
  - other.
  Give exact text.
- **U2.** The nine OUT_OF_ROUND candidates. The seal is meant to refuse contract violations "before derived arithmetic". Do any of these rows (INV-23/36/37/38/52) have to become seal-owned before A291 can merge? Or are they correctly replay-owned, with the merge-time guarantee resting on replay? This also decides ex-101 F2's requested oracle-gap rule for these candidates. Rule whether each is refutable from the amended contract.
- **U3.** Anything else before the final pass on the merge candidate.

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`.
- Never touch `/Users/edr/code/JouleWise`, `/Users/edr/night-custody`, `/Users/edr/JouleWise-measurement-*` or `~/Library/LaunchAgents`.
- Code evidence comes from `git show 6e2504b1:<path>` and `git show 36e470ca:<path>`, or from `/tmp` archive probes. You may re-run `ex-104-adjudicate.py`; it needs the forger scripts in `/tmp/forger-278ebc9e-fable`.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, memory, or `docs/process_traces` files outside this packet directory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
adf484bb9b4c74c56b2ea299f4beb6863752f7deac4441b795852fff9bfcf088  ex-101-forger-ruling.md
2645cab9e669d0fce4d0327e727ec4f1560649304544ee64ef8b1b9be74b0cc6  ex-102-brief.md
6a480baf9351ac1a90822680a6d95dcad7f2fa41a64e28c795d157b5729f703f  ex-102a-brief-rephrased.md
ddd21384ae8478a3a1b814c377c415d2a7451c2e7f725611e940af2f99a46399  ex-103-fa-runs-summary.txt
c5ba2e804decffb47c41c76afbcbdaee4b3a0b2a129582e646b9ecacb3a0ba0f  ex-103b-fa-run2.md
dc065bf7ed7baffe9e218faa9a4a0bb9c737e767e00bcc76b48bd4a0be64222e  ex-104-adjudicate.py
74f939a525f502f1b24286e3e4e150c116d9dff6f9a6240045cfd24a66a0d9aa  ex-104-fc-adjudication.jsonl
84259a80e7eb2d5958f56f7a3e5c0e8003caf6cfecfc1b55d9e7620710d58d50  ex-104-fc-report.md
63787c28d620c4811b327b85cf7d57db12eddf29aa40a0d17337ec87affd9b87  ex-95-texts-r4b.md
```
