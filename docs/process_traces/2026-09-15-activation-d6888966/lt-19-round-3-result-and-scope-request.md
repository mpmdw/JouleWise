# lt-19 — Round 3 landed `d74b5ff1`; delta 3 HELD on a one-file scope grant

Written 11:04 PDT 2026-09-15 (clock read).

## Round 3 is implemented, and the three dictated edits are in

Seat 1 (Astra xhigh, pid 80476, 10:36:27 → 10:49) implemented edits 2 and 3 and
returned two `NEEDS_RULING`s. Seat 2 (Astra xhigh, pid 89323, 10:51:16 → 11:00)
completed edit 1 on top of the same uncommitted tree. Landed together as
**`d74b5ff1`**, pushed.

Lead-run at that head: `test_install_night_agent` **OK**,
`test_magistrate_watchdog` **OK**, `test_night_gate` **OK**,
`test_docs_freshness` **OK**. Runbook §3 byte-identical. All four dictated
mutations RED. Nine-cell teardown matrix unchanged at 143/130/129/1/3/3/3/2/4;
the five commit-gate cases, the render-only cases and every FIX-1..FIX-10
regression still pass.

## NEEDS_RULING F1 — ruled by the lieutenant: regression (ii) is a CONTROL

The dictation said both edit-1 regressions must be "RED at `9a7bacdf`, GREEN
after". The seat held edit 1 because **(ii) already passes at `9a7bacdf`** —
clock advance during backup removal gives rc 0, both loaded, both plists, no
backup dir. It is right, and the cold gate's own probe Q1a recorded exactly that
result at this head and ruled it the INTENDED installed state.

**Ruled: (ii) is a control that must pass before AND after**; only (i) is the
RED-before/GREEN-after regression. The "RED at 9a7bacdf" phrase belonged to (i)
and I carried it across both. No dictated production edit changed. The seat then
reported (ii) passing against both the unmodified `9a7bacdf` installer and the
edited one, and (i) going from rc 1 to rc 0.

This is the fourth dictation defect of mine that a seat has caught by refusing
to guess. The early-return protocol is carrying this lane.

## NEEDS_RULING F2 — NOT mine to rule. **This is the ask.**

`tests/test_run_night.py` contains two tests —
`test_installer_uninstalls_with_stale_courier_sent` and
`test_installer_uninstalls_without_courier_on_minimal_path` — whose launchctl
stub is:

```
#!/bin/zsh
print -r -- "$*" >> "$LAUNCH_LOG"
exit 0
```

It answers **every** call rc 0, including `print`. Under the dictated uninstall
block that means "both labels are still loaded after bootout", so the installer
correctly exits 4 and both tests fail. **The stub is unfaithful**: a real
`launchctl print` after a successful bootout returns non-zero. The production
code is right and the tests encode an impossible launchd.

The cure is small and mechanical, in ONE file outside the granted WRITE_SCOPE:
make the stub answer `print` non-zero (or track bootouts), leaving both tests'
actual assertions intact.

**I did not grant this myself.** The Opus pairing refuter's line on the earlier
uninstall expansion is categorical — *"WRITE_SCOPE expansion + an amended scope
note, the magistrate's to grant, never the lieutenant's"* — and my direction
names the three files as "exactly". Weakening the uninstall block to satisfy a
stale stub was the other option and it would revert the ruling, so it was
forbidden to the seat and is forbidden to me.

**Requested: extend this lane's WRITE_SCOPE by `tests/test_run_night.py`,
limited to the launchctl stub in those two tests.**

## Why I have NOT started delta 3

`int/2026-09-15-install-windows` at `d74b5ff1` is **knowingly red on
`tests.test_run_night` (2 failures)** and green everywhere else. I committed and
pushed it anyway, documented in the commit message, because it is a pre-merge
integration branch and the work is worth durable storage — but I will not spend
a delta auditor on a head whose module set I already know to be red for a reason
that has nothing to do with what the auditor must judge. Its verdict on the two
stop-condition predicates would be entangled with two failures I can explain in
one sentence.

Delta 3 starts the moment the scope is granted and the stub is faithful. Its
brief is already written and will carry, as directed: isolated reversion of each
of the three edits; the same-signature question answered ONLY by the two
executed predicates in synthesis 13 §Q3; and a by-name re-run of lt-04 §F4's 22
survivors and lt-10's 8 teardown + 3 tail survivors, with both lists supplied
verbatim in the brief and the must-die set from synthesis 13 §Q5.

## Standing item the magistrate still needs to place

`scripts/install_magistrate_watchdog.sh:199-201` has the same
`bootout … || true; rm -f; exit 0` shape for the magistrate's own agent (Opus
refuter, MATERIAL, read not probed). Round 3 was forbidden to touch it. Until a
lane covers it, class 2 is closed for the night agent and open for the watchdog
agent — "the class closes half-way" in the refuter's words.
