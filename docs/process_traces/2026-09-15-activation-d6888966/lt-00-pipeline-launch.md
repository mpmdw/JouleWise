# lt-00 — Opus lieutenant: INSTALL-WINDOWS-MULTI-01 review gauntlet, launch record

Activation `d6888966`. Written 07:10 PDT 2026-09-15 (clock-read). The lieutenant
directs the gauntlet; the magistrate opens and merges the PR. Nothing here
amends a rule.

## Tree state at pipeline start (lead-verified, not taken from a report)

- Integration worktree `/Users/edr/code/JouleWise-wt-integ-install-windows`,
  branch `int/2026-09-15-install-windows`.
- Inherited head `1cc8db30` = seat A `33bdc457` + `origin/main 664b3f6c` + seat D
  `d49c0b9b` (harvest record 07).
- `origin/main` had advanced to `e42949dc` (trace/bookkeeping commits only:
  records 02–07, their manifests, the 09-02 DURABLE-STATE pointer, and the
  PACK-ROOT status note). Merged into the int branch at 07:0x so the refuters'
  three-dot base is the live main: **`5124de47`**.
- Integrated diff at that head: 14 files, +927 / −338
  (`configs/launchd/com.joulewise.night.plist.template`, four scripts, four test
  modules, four process/runbook documents, and the generated
  `SHAKEDOWN-G2-RUNSHEET.md` region).
- `scripts/shard_tests.py` EXISTS on the tree, so the step-4 replay uses it.

## Authority read before acting

`docs/process_traces/2026-09-15-activation-1acf2aee/06-design-adjudication-install-windows.md`;
kernel row `INSTALL-WINDOWS-MULTI-01` `acceptance.summary`; D-180 cl.1 / D-181
cl.1 as carried in that row's `authority`; seat reports 02 and 03; harvest
record 07. `CLAUDE.local.md` rule 11's forbidden list was read before any seat
was launched.

## Pipeline

| Step | Seat | Model / effort / sandbox | Record |
|---|---|---|---|
| 1 | Docs↔code reconciliation | Astra high, workspace-write, int worktree | `lt-01` |
| 2a | Refuter, CONTRACT lens | Astra xhigh, read-only, `wt-ref-iw-contract` (detached) | `lt-02` |
| 2b | Refuter, EXECUTION lens | Astra xhigh, workspace-write, `wt-ref-iw-execution` (detached, disposable) | `lt-03` |
| 3 | Fix rounds + delta re-audit | Astra high / fresh read-only Astra | `lt-04+` |
| 4 | Replay at the final head | lead-run, unpiped | in the ledger record |
| 5 | Twelve-row ledger + PR body draft | lead | `lt-90`, `lt-91` |

### Recorded deviation: the execution refuter's sandbox

The direction specified read-only for both refuters. The execution lens is
required to mutate code, build fake-`launchctl` sandboxes and run a rendered
installer; record 04 of this activation is direct evidence that a read-only
Astra seat cannot do that work (its Q2/Q5 were "blocked by the read-only
sandbox"). The seat was therefore relaunched (07:10:01) with `workspace-write`
in its DISPOSABLE detached worktree, under an added brief clause requiring every
mutation to happen in a `/tmp` copy, byte-identical restoration of anything
touched in place, and an EMPTY `git status --porcelain` pasted as its final
verification entry. The integration tree is untouched by it and nothing is ever
committed from that worktree. This is a mechanism choice inside the lieutenant's
remit, not a change to any rule; it is flagged here and in the handback so the
magistrate can overrule it.

## Standing constraints honoured

No git in the canonical root `/Users/edr/code/JouleWise`. Nothing under
`/Users/edr/night-custody`, `~/Library/LaunchAgents`, or
`/Users/edr/JouleWise-measurement-*` is read or written by any seat. No real
`launchctl` bootstrap. No merge, no PR, no edit to `docs/decision_log.md`, the
skills, or any process doc outside the four reconciliation paths. All
timestamps are clock reads.
