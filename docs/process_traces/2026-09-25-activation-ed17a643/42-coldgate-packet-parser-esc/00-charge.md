# Charge: cold gate BFG-D-PARSER-ESC-01. Rule the structural parser cure and the plan for fix round 2 of BFG-D.

Assembled 2026-09-25 ≈20:55 PDT by the resident magistrate (Opus 5.5, activation ed17a643). Nothing is armed. **Mandatory trigger (rule 11):** this would be a second fix round on the same defect. **Standing escalation:** the same signature has now appeared in two consecutive rounds.

## Background

BFG-D (branch `origin/feat/2026-09-25-bfg-d`, fix round 1 at `faf0ea01`) implements Ed's binding battery-float directive #421 for derivation windows. The next window, W1, waits on it.

The battery predicate parses the TEXT output of the registered probe `/usr/sbin/ioreg -r -c AppleSmartBattery`, whose raw stdout is retained and hashed. Registration A-R5b (PR #423) names that exact command.

The parser has now failed review twice with the same defect class: it accepts structurally wrong output as a pass.
- In round 1, three cases reached GO: a missing closing brace, a different object class, and required keys present only inside a nested dictionary.
- In the fix-round-1 delta (ex-05, Astra B1), two more were found. The header regex accepts `<class OtherBattery, ...>`, and nested-depth tracking returns to top level too early.

The same delta found three further items:
- Sol F1 (ex-04, BLOCKER): `scripts/epoch_equivalence_check.py` reads member evidence, B included, with no battery-verdict gate. Revision 5 says the equivalence path is not taken for this epoch.
- Astra M1 (MATERIAL): the dry run swallows `NoRecord` for computed sessions.
- Sol F2 = Astra M2 (MATERIAL): two runbook `check` invocations lack the new flags.

Two blind consults then designed a fail-closed whitelist grammar (ex-01 Sol 6.0 high, ex-02 Astra 6 high). Both prototyped it against the real capture (ex-03), and both advise against changing the registered argv to `-a` without the owner's approval. They are arguments, not authorities.

## Questions

- **E1.** Verify the round-2 parser defects yourself at `faf0ea01`, and verify that each consult's grammar accepts ex-03 and refuses every counterexample it lists. Execute this in a /tmp scratch copy.
- **E2.** Issue the parser grammar as exact final text: regexes or pseudocode, the refusal classes, and the test list. It must be fail-closed by construction, with no depth-tracking heuristics. Say whether the owner should be asked to approve `-a` (plist) for a later amendment. It is not required for W1.
- **E3.** Rule the other delta items: Sol F1 (`epoch_equivalence_check`: refuse Revision-5 sessions outright, or gate them?), Astra M1 and the runbook flags. Give closure shapes and tests.
- **E4.** Issue the fix-round-2 plan: an ordered list of obligations with RED-then-GREEN tests, and a same-signature sweep obligation that names every reader of B-bearing evidence and every consumer of the verdict. Add a plain summary for Ed of at most 5 lines.

## Constraints

- Work in one foreground session. Start no background tasks or subagents. Ending before the ruling file exists is a protocol failure. Budget about 25 minutes.
- Read-only, except /tmp scratch space, which you remove afterwards. No sudo, launchctl, powermetrics, installer runs or model inference. `ioreg` (read-only) is allowed.
- Never touch `/Users/edr/code/JouleWise`, `/Users/edr/night-custody` or `~/Library/LaunchAgents`. Focused unit tests only; no test discovery.
- Write only `20-coldgate-fable-parser-esc-ruling.md` in this packet directory.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory, or `docs/process_traces` files outside this packet, except those under `docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/` on the BFG-D branch and the two earlier packets `../10-coldgate-packet-bfg/` and `../41-coldgate-packet-harvest-final/`.
- Begin with a contamination disclosure.

Charter: `docs/process/coldgate_charter.md` sha256 `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`.

## Exhibit manifest
```
227be197fbba45aa8507608ac4b4eb7f3748bb5f44a881936a6e238207321b80  ex-00-consult-brief.txt
9afe192b42bba911143365684b585a9f897e2461cfa37e7f24eedc541c2d1a38  ex-01-seat-sol.md
d7c42497db212d9af60ae45b7bce9fcbb88f977d5064dbca713ea8b27a2d4d5a  ex-02-seat-astra.md
582475270c35c51cc05c2020f500d8c7dfba3eb9a6436a0186cb5ce18a851631  ex-03-real-ioreg-capture.txt
ffee9d0567d8903159b6fc987dd198b237df43ff21e6281da177f0a1c8708923  ex-04-sol-delta.md
63e6def888e5f631f64a791a55332edad048ed5172b0c896ec3ce492037cf521  ex-05-astra-delta.md
```
