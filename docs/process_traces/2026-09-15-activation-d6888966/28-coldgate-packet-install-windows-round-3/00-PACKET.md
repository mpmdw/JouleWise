# Cold-gate packet 28 — INSTALL-WINDOWS-MULTI-01 after fix round 2 under ruling 10: the delta answers same-signature YES again; F1 cure shape, F2 scoping, round-3 authorization and stop condition (assembled mechanically by activation d6888966, 2026-09-15 10:18 PDT)

Convened under rule 11: a third fix round on the same installer is "any second fix round on the same defect" (mandatory), and the standing escalation trigger fired a second time (exhibit A §SAME-SIGNATURE). Integration head `9a7bacdf` on `int/2026-09-15-install-windows` (this checkout) = round 2 (`cb35e9aa` commit gate + verified-bootout teardown; `5649d494` render-only exemption; `9dc36e53` runbook `:1297`) + merge of main. Ruling 10 (exhibit E) as amended (F, G) was applied; both isolated reversions behave correctly (exhibit A §reversions). No PR, nothing merged, nothing armed.

## What was found (exhibits A, B; the judge verifies on this checkout)

- **F1 (blocker, new this round):** `scripts/install_night_agent.sh:372` commit gate → `:373` success `print` → `:374` `rm -rf "$plist_backup" || exit 1`, with `trap teardown EXIT` (`:342`) still armed. (a) A clock advance during that `rm` ends rc=0 with both jobs loaded at close; the backup lives under `TMPDIR` and its removal mutates no launchd state — whether that is class 1 proper or a definition of "mutation" is for the judge. (b) A failed `rm` exits 1 AFTER success printed; teardown sees non-zero and boots out a correctly installed, verified night. The lieutenant did not apply the one-line cure; that cheapness is the reason.
- **F2 (blocker, pre-existing, outside every brief and recorded "unchanged" by exhibit H):** `--uninstall` at `:267-272` swallows both bootout failures (`|| true`), removes both plists unconditionally, exits 0 — with fake bootouts returning 1 and both jobs loaded: rc 0, plists gone, `installed_agent_fence()=None`. Class 2 at a site ruling 10 Q3 did not reach. It runs in the real harvest flow after every night. FIX-4 (exhibit C/D) makes the installer refuse occupied labels — the judge checks what a stuck loaded job would do to the NEXT install (refusal vs double-arm).
- **F3/F4 (should-fix, pre-existing):** a signal during plist restoration loses un-restored prior bytes (`:332-345`); the backup `cp` precedes trap installation (`:304-309`).
- **Mutation sweep (exhibit A):** 8 survivors in `teardown`, 3 in the production tail; the round-1 22-survivor list was not re-run.
- **Lieutenant rulings in round 2 (exhibit D):** (1) mutation oracle replaced by "final four launchctl calls are bootout/bootout/print/print with nothing after, and the stub asserts both plists exist when bootout is called"; (2) `exit 4` instead of `return 4` from the EXIT-trap function (measured: `return` does not set the process status on zsh 5.9); (3) `--render-only` teardown does file restore/removal only, zero launchctl calls (a failed render-only had booted out labels belonging to another install).

## Q1 — F1 cure shape (rule one, or write a better one)

(a) Incomplete application of ruling 10 Q3 step 1 ("in every case `rm -rf "$plist_backup"`" belongs to `teardown`): delete `:374`; `teardown` on `result == 0` removes the backup and returns 0 without touching launchd; nothing failable follows the success `print`; regressions: clock advance injected during backup removal → rc 0, both loaded, both plists present, no backup dir; injected backup-removal failure after success → rc 0 (or a documented non-zero that does NOT tear down), both loaded, both plists present. (b) A new class requiring further restructure (say what). Also rule the definition: does the class-1 invariant cover launchd mutations only (so (a)'s clock case is the intended installed state) or every statement before exit?

## Q2 — F2 scoping (rule one)

(i) Blocks this lane; cure it in round 3 under a scope expansion using the teardown discipline (bootout both, re-read `launchctl print`, refuse to delete a plist under a still-loaded job, distinct non-zero exit), with a regression mirroring cell 9. (ii) Its own registered lane (UNINSTALL-VERIFIED-BOOTOUT-01), this lane lands without it; state the risk with the FIX-4 occupied-label refusal verified. (iii) Other. Say whether (i) is a contract change to exhibit H ("uninstall unchanged").

## Q3 — round 3 authorization and the stop condition

Charter §9: another same-shape round needs explicit justification. Is round 3 justified (dictated one-line cures for F1 (+F2 if Q2 = i), no new structure)? State the STOP CONDITION now: if delta 3 answers same-signature YES again, what happens — land with the residue as registered lanes, restructure the installer (e.g. a Python state machine with one transactional commit), or escalate to Ed — and who decides.

## Q4 — F3/F4

Fold into round 3 (give the closure shape) or register as a lane; which, and why.

## Q5 — survivors

Of the 8 `teardown` and 3 production-tail mutation survivors in exhibit A §Mutation sweep, which must die before landing (name them) and which are diagnostic-text only.

## Q6 — the lieutenant's three round-2 rulings (exhibit D)

For each: AFFIRM / AMEND (exact text) / REFUSE. In particular (3): is a render-only run that never touches launchd the correct contract, and must the installer refuse render-only when either label is already loaded?

## Constraints on the judge

Rule only the questions above; do not amend any rule, decision-log entry or skill doctrine (name text changes as text for the magistrate to record). Cite exhibits by name; code by file:line only if you read it in this checkout (`9a7bacdf`). Execute at least one probe for Q1 and one for Q2 with the fake-launchctl pattern of `tests/test_install_night_agent.py` (never a real `launchctl bootstrap`; never touch `~/Library/LaunchAgents` or `/Users/edr/night-custody`). Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE.local.md or narrative state docs. Under 14 KB. Ending before the ruling file exists is a protocol failure.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
38306d10742c5ebb481f2760a9d0fd4e13a8a0707aba01cabfa49edbac363a91  exhibit-A-delta-2-lt15.md
0363ffd500728fb736615a6da9a46696f5c52cd0e4fe1e2d6ac2b6b55ef94b99  exhibit-B-second-stop-lt16.md
955d26c9b2305a6627a4134a2c27994b8a4af6768ec7fe938bebbfd6b1c337bd  exhibit-C-fix-round-2-contract-lt13.md
b41fb6fd9313db25176bc26f5b18d848fdd24793613f9408e580b59523006c64  exhibit-D-round-2-rulings-lt14.md
4cb14fdc5164ce994861c750e1f576a7866c7916817ae2e5149ad20c146b0af0  exhibit-E-ruling-10.md
b31765c08456cb9fe7c1cc208310a83db6ced3c08281324b4f821c4a705938f5  exhibit-F-opus-pairing-12.md
31a3133d35a2abffac888f220a1379b4a4efd6522c6a0c25348f452b006fc37e  exhibit-G-synthesis-13.md
cb101bd2a0d32c385848f118b8401fb73dbabb1b20ac29b18d38b2af16e5d8a4  exhibit-H-design-adjudication-06.md
```
