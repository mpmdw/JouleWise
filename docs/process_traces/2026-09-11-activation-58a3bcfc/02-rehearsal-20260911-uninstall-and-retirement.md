# 02 — rehearsal-20260911 uninstall and retirement — 2026-09-11 07:12–07:14 PDT, activation 58a3bcfc

Checklist 13 step 4, after record 01's evidence preservation and acceptance disposition.

Process clearance (07:12): courier pid 38007 gone; dead-man courier-lock pid 37846 gone; no `run_night.py` process; `night/` holds no `chain.started` (the chain never started, so no chain or campaign ownership exists under `docs/contracts/window_liveness.md`); `active-campaigns/` empty.

Uninstall, run FROM the stub checkout `/private/tmp/joulewise-rehearsal-20260911-checkout` at 57ddad20 (verified `$PWD` and HEAD before the call):

```
scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260911/night_plan.json --hour 2 --minute 56 --uninstall
UNINSTALL_RC=0
```

`launchctl list` before: `com.joulewise.night` (last exit 1 — the 02:56 crash), `com.joulewise.night.deadman` (0). After: no `com.joulewise.night*` label; both plists removed from `~/Library/LaunchAgents` (only `com.joulewise.magistrate.plist` remains).

Guarded removal (the checklist's sequence, run from the bookkeeping worktree, never the canonical root): archive `/Users/edr/night-custody-archive/rehearsal-20260911-harvest-58a3bcfc` re-checked (`night_plan.json` + `night.log` present; no night labels loaded; `diff -qr` against the live root IDENTICAL) → `git worktree remove /private/tmp/joulewise-rehearsal-20260911-checkout` rc 0 (path gone, no worktree entry remains) → `rm -rf /Users/edr/night-custody/rehearsal-20260911` (gone). `find ~/night-custody -maxdepth 2 -name night_plan.json` returns nothing: NOTHING IS ARMED; the frozen-checkout list for the next relaunch is the canonical repo only.

Orphan daemon tree (record 01 F2) still alive at this write — not cleared by this activation (permission classifier denial); Ed-external.

State of NIGHT-REHEARSAL-01 after this night: item 1 CLOSED (derivation 70 / capture 104); item 5 MET (this night, record 01); items 4 and 6 OPEN; item 6 needs a non-refused night after the interpreter cure (NIGHT-INTERPRETER-PIN-01). Whether that must be another REHEARSAL_STUB night or may be the equivalence night itself (runbook §2.5) is a cold-gate question, not decided here.
