# PACKET INDEX — recorder-race cold gate (WO-MARGIN-RECORDER-AUTHZ)

Assembled by `assemble.py` in this directory (non-author assembly; run it to regenerate).
Repo head at assembly: `a2d4d048bee5fe78ae6514e2f5587f71f0564aa3`; reviewed branch `impl/wo-margin-recorder-authz` at
`eff85f8da7ca31301121aa5f47c16c9e43f00573`.

## Contents and what each primary is FOR

| # | Primary | Source + extraction rule | What it is FOR |
|---|---------|--------------------------|----------------|
| 1 | Review F1 + "Other attack lines passed" | `sol-recorder-review.md` lines 111-138; `^### F1 ` heading span to next `^## ` | Establishes the ORIGINAL defect class (grant escapes the selected-path boundary via aliasing) and, critically, the NEGATIVE space: the attack lines that already pass, so the pairing can see what round 2 must not regress. |
| 2 | Fix round 1 commit | `git show --format=fuller eff85f8` | The code actually under review — the resolution-invariance guard and its regression. Lets the pairing judge round 1 on the diff rather than on either party's description of it. |
| 3 | Delta re-audit verdict, F1, residual risk | `sol-recorder-delta.md`: envelope keys `status`/`completion`/`summary`/`verdict`/`flags`, plus verbatim `## Findings` and `## Residual risk` spans | The independent finding that round 1 left a check-to-grant race — i.e. the second fix round's justification. The `flags` key is included so the pairing sees that this audit is `completion='partial'` with a BLOCKING verification gap, rather than reading its REJECT as fully demonstrated. |
| 4 | Magistrate round-2 proposal | `recorder-round2-proposal.md`, full file | The design under adjudication (content-binding closure + fd-identity alternative + the reviewed party's own severity framing). LABELED as the reviewed party's submission; it is the thing to be ruled on, not evidence for it. |
| 5 | Threat-model primary | `docs/contracts/calibration_ledger.md`, first 10 lines | The contract's own statement that it "does not defend against a malicious trusted writer". This is the text that decides question 1 (is a concurrent local adversary in-model), and therefore whether `blocker` is the right severity. |
| 6 | Adoption ruling | `docs/decision_log.md` lines 9056-9094, heading span | The boundary the defect violates: clause 1's exhaustive never-granted list and the narrower-than-mint invocation shape; clause 2's "no change to `joulewise/authentication_io.py` or any public API", which is the constraint PRIMARY 4 designs around. Fixes the question of what round 2 is even allowed to touch. |
| S1 | F2 threat table (MECHANIC ADDITION) | `docs/process_traces/2026-08-15-recorder-authz-consult/consult.md` lines 148-166, `^### F2 ` heading span | The required-result table PRIMARY 1 convicts the code against, which the assembly order left as a dangling citation. It is the closest thing the instrument has to a written threat enumeration, so it is second evidence on question 1 alongside PRIMARY 5. |

## Flagged gaps, hand-selections, and anomalies

No silent gaps. Everything below was detected or declared during assembly:

1. P1: the review's line citations point at a TEMPORARY review checkout under the session scratchpad (/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/review-recorder/...), not at repository paths. Those links are not resolvable from the repo; the corresponding repo file is joulewise/window_duration_margins.py on impl/wo-margin-recorder-authz.
2. P3: the delta re-audit is completion='partial' - it is NOT a complete audit. Its own confirming mutation (V5, guard removal) was sandbox-blocked and reported not_run.
3. P3: delta flag G1 is BLOCKING (verification_gap): The mandatory guard-only mutate-and-check could not be executed because apply_patch was forbidden in the clean temporary export; the repository checkout could not be mutated under WRITE_SCOPE [].
4. P5 is a HAND-SPECIFIED WINDOW: the first 10 lines of docs/contracts/calibration_ledger.md, chosen by the assembly order, not by a heading rule. It is an excerpt of a longer contract; the pairing should read the full file if the trusted-writer boundary is load-bearing to its ruling.
5. P6: the WO-MARGIN-RECORDER-AUTHZ decision-log entry has an 'M-2 GATE AMENDMENT' block appended INSIDE it that concerns a different instrument (the M-2 draft_status override), not this work order. It is reproduced verbatim because the entry has no internal heading to cut at - it is NOT part of the recorder authorization ruling.
6. SUPPLEMENT S1 IS A MECHANIC ADDITION beyond the six-primary assembly order: the F2 threat table from docs/process_traces/2026-08-15-recorder-authz-consult/consult.md lines 148-166. Reason: PRIMARY 1 convicts the code against this table, which the order did not attach. Extracted by heading span, not hand-picked rows.

## Deliberate scope limits of this packet (mechanic's declaration)

- **Not attached:** the WO-MARGIN-RECORDER-AUTHZ consult trace
  (`docs/process_traces/2026-08-15-recorder-authz-consult/`), which PRIMARY 6 names as the ONE
  home for the mechanism detail, and the current text of
  `joulewise/window_duration_margins.py`. Both are in the repo and readable by the seats; the
  assembly order enumerated six primaries and this script attaches exactly those six. The
  pairing should read the live file before licensing an exact specification.
- **Attached beyond the order:** the F2 threat table (SUPPLEMENT S1) — see the anomaly list.
  Nothing else was added.
- **Round 2 is unimplemented.** There is no round-2 diff to attach; PRIMARY 4 is a design
  statement, and the gate sits BEFORE the implementation by rule-11 order.
- **The mechanic did not verify any claim in any primary.** This is an assembly record. The
  seats verify against the live repo.
